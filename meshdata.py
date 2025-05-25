import configparser
import mysql.connector
import datetime
import json
import time
import utils
import logging
import re
import meshtastic_support


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        # Use default serialization for other types
        return super().default(obj)


class MeshData:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.config = config
        self.db = None
        self.connect_db()

    def __del__(self):
        if self.db:
            self.db.close()

    def int_id(self, id):
        try:
            id = id.replace("!", "")
            return int(f"0x{id}", 16)
        except Exception as e:
            pass
        return None

    def hex_id(self, id):
        return utils.convert_node_id_from_int_to_hex(id)

    def unknown(self, id):
        hexid = self.hex_id(id)
        short_name = hexid[-4:]
        long_name = f"Meshtastic {short_name}"
        return {
            "from": id,
            "decoded": {
                "json_payload": {
                    "long_name": long_name,
                    "short_name": short_name
                }
            }
        }

    def connect_db(self):
        self.db = mysql.connector.connect(
            host=self.config["database"]["host"],
            user=self.config["database"]["username"],
            password=self.config["database"]["password"],
            database=self.config["database"]["database"],
            charset="utf8mb4"
        )
        cur = self.db.cursor()
        cur.execute("SET NAMES utf8mb4;")


    def cleanup_nodes(self):
        try:
            sql = """
            DELETE FROM nodeinfo
            WHERE ts_seen < NOW() - INTERVAL 10 DAY
            """
            cur = self.db.cursor()
            cur.execute(sql)
            affected_rows = cur.rowcount
            self.db.commit()
            cur.close()
            logging.info(f"Deleted {affected_rows} old nodes from nodeinfo.")
        except Exception as e:
            logging.error(f"Error cleaning up old nodes: {e}")


    def get_node_activity(self):
        activity = {}
        try:
            sql = """SELECT 
                        JSON_EXTRACT(message, '$.from') AS node_id,
                        JSON_EXTRACT(message, '$.to') AS to_id,
                        MAX(JSON_EXTRACT(message, '$.rx_time')) AS last_activity
                     FROM meshlog
                     WHERE ts_created >= NOW() - INTERVAL 15 SECOND
                     GROUP BY node_id, to_id;"""
            cur = self.db.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                node_id, to_id, last_activity = row
                if node_id and last_activity:
                    activity[utils.convert_node_id_from_int_to_hex(int(node_id))] = {
                        "to": utils.convert_node_id_from_int_to_hex(int(to_id)) if to_id else None,
                        "last_activity": int(last_activity)
                    }
            cur.close()
        except Exception as e:
            logging.error(f"Error fetching node activity from meshlog: {e}")
        return activity

    def get_telemetry(self, id):
        telemetry = {}
        sql = """SELECT * FROM telemetry WHERE id = %s
AND battery_level IS NOT NULL
ORDER BY telemetry_time DESC LIMIT 1"""
        params = (id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            for i in range(1, len(row)):
                if isinstance(row[i], datetime.datetime):
                    telemetry[column_names[i]] = row[i].timestamp()
                else:
                    telemetry[column_names[i]] = row[i]
        cur.close()
        return telemetry

    def get_telemetry_all(self):
        telemetry = []
        sql = """SELECT * FROM telemetry
WHERE battery_level IS NOT NULL OR temperature IS NOT NULL
ORDER BY ts_created DESC LIMIT 500"""
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            record = {}
            column_names = [desc[0] for desc in cur.description]
            for i in range(0, len(row)):
                if isinstance(row[i], datetime.datetime):
                    record[column_names[i]] = row[i].timestamp()
                else:
                    record[column_names[i]] = row[i]
            telemetry.append(record)
        cur.close()
        return telemetry

    def get_node_telemetry(self, node_id):
        telemetry = []
        sql = """SELECT * FROM telemetry
WHERE ts_created >= NOW() - INTERVAL 1 DAY
AND id = %s AND battery_level IS NOT NULL
ORDER BY ts_created"""
        params = (node_id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        for row in rows:
            record = {}
            column_names = [desc[0] for desc in cur.description]
            for i in range(0, len(row)):
                if isinstance(row[i], datetime.datetime):
                    record[column_names[i]] = row[i].timestamp()
                else:
                    record[column_names[i]] = row[i]
            telemetry.append(record)
        cur.close()
        return telemetry

    def get_node_env_telemetry(self, node_id):
        telemetry = []
        sql = """SELECT * FROM telemetry
WHERE ts_created >= NOW() - INTERVAL 1 DAY
AND id = %s AND temperature IS NOT NULL
ORDER BY ts_created"""
        params = (node_id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        for row in rows:
            record = {}
            column_names = [desc[0] for desc in cur.description]
            for i in range(0, len(row)):
                if isinstance(row[i], datetime.datetime):
                    record[column_names[i]] = row[i].timestamp()
                else:
                    record[column_names[i]] = row[i]
            telemetry.append(record)
        cur.close()
        return telemetry

    def get_position(self, id):
        position = {}
        sql = "SELECT * FROM position WHERE id = %s"
        params = (id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            for i in range(1, len(row)):
                if isinstance(row[i], datetime.datetime):
                    position[column_names[i]] = row[i].timestamp()
                else:
                    position[column_names[i]] = row[i]
        cur.close()
        return position

    def get_neighbors(self, id):
        neighbors = []
        sql = """SELECT
    a.id,
    a.neighbor_id,
    a.snr,
    p1.latitude_i lat1_i,
    p1.longitude_i lon1_i,
    p2.latitude_i lat2_i,
    p2.longitude_i lon2_i,
    a.ts_created
FROM neighborinfo a
LEFT OUTER JOIN position p1 ON p1.id = a.id
LEFT OUTER JOIN position p2 ON p2.id = a.neighbor_id
WHERE a.id = %s
AND a.ts_created > (NOW() - INTERVAL 3 DAY)
"""
        params = (id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        for row in rows:
            record = {}
            for i in range(1, len(row)):
                if isinstance(row[i], datetime.datetime):
                    record[column_names[i]] = row[i].timestamp()
                else:
                    record[column_names[i]] = row[i]

            if record["lat1_i"] and record["lon1_i"] and \
                    record["lat2_i"] and record["lon2_i"]:
                distance = round(utils.distance_between_two_points(
                    record["lat1_i"] / 10000000,
                    record["lon1_i"] / 10000000,
                    record["lat2_i"] / 10000000,
                    record["lon2_i"] / 10000000
                ), 2)
            else:
                distance = None
            record["distance"] = distance
            del record["lat1_i"]
            del record["lon1_i"]
            del record["lat2_i"]
            del record["lon2_i"]
            neighbors.append(record)
        cur.close()
        return neighbors

    def get_traceroutes(self):
        tracerouts = []
        sql = """SELECT from_id, to_id, route, snr, 
    FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(ts_created) / 3) * 3) AS ts_grouped
FROM traceroute
WHERE snr IS NOT NULL
GROUP BY 
    from_id, 
    to_id, 
    route, 
    snr, 
    ts_grouped
ORDER BY ts_grouped DESC
LIMIT 100"""
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            tracerouts.append(
                {
                    "from_id": row[0],
                    "to_id": row[1],
                    "route":
                        [int(a) for a in row[2].split(";")] if row[2] else [],
                    "snr":
                        [int(s) / 4 for s in row[3].split(";")] if row[3] else [],
                    "ts_created": row[4].timestamp()
                }
            )
        cur.close()
        return tracerouts

    def get_nodes(self, active=False, with_neighbors=True, with_position=True):
        nodes = {}
        active_threshold = int(self.config["server"]["node_activity_prune_threshold"])
        base_sql = """
SELECT 
    n.*, 
    u.username AS owner_username,
    IF(
        t.id IS NOT NULL,
        JSON_OBJECT(
            'id', t.id,
            'air_util_tx', t.air_util_tx,
            'battery_level', t.battery_level,
            'channel_utilization', t.channel_utilization,
            'uptime_seconds', t.uptime_seconds,
            'voltage', t.voltage,
            'temperature', t.temperature,
            'telemetry_time', UNIX_TIMESTAMP(t.telemetry_time),
            'ts_created', UNIX_TIMESTAMP(t.ts_created)
        ),
        JSON_OBJECT()
    ) AS telemetry
FROM nodeinfo n
LEFT JOIN meshuser u ON n.owner = u.email
LEFT JOIN (
    SELECT t1.*
    FROM telemetry t1
    JOIN (
        SELECT id, MAX(telemetry_time) AS max_time
        FROM telemetry
        WHERE battery_level IS NOT NULL
        GROUP BY id
    ) t2 ON t1.id = t2.id AND t1.telemetry_time = t2.max_time
) t ON n.id = t.id
WHERE n.id <> 4294967295
"""
        if active:
            base_sql += " AND n.ts_seen > FROM_UNIXTIME(%s)"

        cur = self.db.cursor()
        if active:
            timeout = time.time() - active_threshold
            cur.execute(base_sql, (timeout,))
        else:
            cur.execute(base_sql)

        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        node_ids = []
        for row in rows:
            record = {}
            for i in range(len(row)):
                if isinstance(row[i], datetime.datetime):
                    record[column_names[i]] = row[i].timestamp()
                else:
                    record[column_names[i]] = row[i]
            is_active = record["ts_seen"] > (time.time() - active_threshold)
            record["telemetry"] = json.loads(record["telemetry"]) if record["telemetry"] else {}
            record["role"] = record["role"] or 0
            record["active"] = is_active
            record["last_seen"] = utils.time_since(record["ts_seen"])
            node_id = utils.convert_node_id_from_int_to_hex(row[0])
            nodes[node_id] = record
            node_ids.append(row[0])
        cur.close()

        # Hromadné načtení neighbors a position
        if with_neighbors:
            neighbors_map = {nid: self.get_neighbors(nid) for nid in node_ids}
            for idx, nid in enumerate(node_ids):
                nodes[utils.convert_node_id_from_int_to_hex(nid)]["neighbors"] = neighbors_map[nid]
        if with_position:
            positions_map = {nid: self.get_position(nid) for nid in node_ids}
            for idx, nid in enumerate(node_ids):
                pos = positions_map[nid]
                node = nodes[utils.convert_node_id_from_int_to_hex(nid)]
                node["position"] = pos
                if pos:
                    node["position"]["latitude"] = pos["latitude_i"] / 10000000 if pos.get("latitude_i") else None
                    node["position"]["longitude"] = pos["longitude_i"] / 10000000 if pos.get("longitude_i") else None

        return nodes

    def get_chat(self):
        sql = """SELECT from_id, to_id, channel, text, MIN(ts_created) AS ts_created
FROM text
WHERE to_id = 4294967295
GROUP BY from_id, to_id, channel, text
ORDER BY ts_created DESC
LIMIT 100;"""
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        prev_key = ""
        chats = []
        for row in rows:
            record = {column_names[i]: (row[i].timestamp() if isinstance(row[i], datetime.datetime) else row[i]) for i in range(len(row))}
            record["from"] = self.hex_id(record["from_id"])
            record["to"] = self.hex_id(record["to_id"])
            msg_key = record["from"] + record["to"] + record["text"]
            if msg_key != prev_key:
                chats.append(record.copy())
                prev_key = msg_key
        cur.close()
        return chats

    def get_route_coordinates(self, id):
        sql = """SELECT longitude_i, latitude_i
FROM positionlog WHERE id = %s
AND source = 'position'
ORDER BY ts_created DESC"""
        params = (id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        coords = []
        for row in cur.fetchall():
            coords.append([
                row[0] / 10000000,
                row[1] / 10000000
            ])
        cur.close()
        return list(reversed(coords))

    def get_logs(self):
        logs = []
        sql = "SELECT * FROM meshlog ORDER BY ts_created DESC limit 100"
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        for row in rows:
            record = {}
            for i in range(len(row)):
                col = column_names[i]
                if isinstance(row[i], datetime.datetime):
                    record[col] = row[i].timestamp()
                else:
                    record[col] = row[i]
            logs.append(record)
        return logs

    def get_latest_node(self):
        sql = """select id, ts_created from nodeinfo
where id <> 4294967295 order by ts_created desc limit 1"""
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        latest = {}
        if row:
            latest = {
                "id": row[0],
                "ts_created": row[1].timestamp()
            }
        cur.close()
        return latest

    def get_user(self, username):
        sql = "SELECT * FROM meshuser WHERE username=%s"
        params = (username, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        column_names = [desc[0] for desc in cur.description]
        record = {}
        if row:
            for i in range(len(row)):
                col = column_names[i]
                if isinstance(row[i], datetime.datetime):
                    record[col] = row[i].timestamp()
                else:
                    record[col] = row[i]
        cur.close()
        return record

    def update_geocode(self, id, lat, lon):
        if self.config["geocoding"]["enabled"] != "true":
            return
        update = False
        sql = """SELECT 1 FROM position WHERE
id=%s AND (geocoded IS NULL OR (latitude_i <> %s OR longitude_i <> %s))"""
        params = (
            id,
            lat,
            lon
        )
        cur = self.db.cursor()
        cur.execute(sql, params)
        update = True if cur.fetchone() else False
        geo = None
        cur.close()
        if not update:
            return

        latitude = lat / 10000000
        longitude = lon / 10000000
        geocoded = utils.geocode_position(
            self.config['geocoding']['apikey'],
            latitude,
            longitude
        )
        if geocoded and "display_name" in geocoded:
            geo = geocoded["display_name"]

        sql = """UPDATE position SET
latitude_i = %s,
longitude_i = %s,
geocoded = %s
WHERE id = %s
"""
        params = (
            lat,
            lon,
            geo,
            id
        )
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()
        self.db.commit()

    def graph_nodes(self):
        graph_data = {
            "nodes": [],
            "edges": []
        }
        nodes = self.get_nodes()
        known_edges = []
        known_nodes = []
        for id, node in nodes.items():
            if id not in known_nodes:
                if "neighbors" not in node:
                    continue
                if not node["neighbors"]:
                    continue

                graph_data['nodes'].append(
                    {
                        "id": id,
                        "name": node['long_name'],
                        "short": node['short_name'],
                        "height": 30,
                        "stroke": None,
                        'fill': {"src": utils.graph_icon(node['long_name'])}
                    }
                )
                known_nodes.append(id)
                for neighbor in node['neighbors']:
                    neigbor_id = \
                        utils.convert_node_id_from_int_to_hex(
                            neighbor["neighbor_id"]
                        )
                    edge_key_1 = f"{id}.{neigbor_id}"
                    edge_key_2 = f"{neigbor_id}.{id}"
                    if edge_key_1 not in known_edges and \
                            edge_key_2 not in known_edges:
                        if neigbor_id in nodes:
                            graph_data["edges"].append(
                                {"from": id, "to": neigbor_id}
                            )
                            known_edges.append(edge_key_1)
                            known_edges.append(edge_key_2)
        for edge in graph_data["edges"]:
            to = edge['to']
            to_node = None
            if to in nodes:
                to_node = nodes[to]
            else:
                to_node = self.unknown(self.int_id(to))
            if to not in known_nodes:
                known_nodes.append(to)
                graph_data['nodes'].append(
                    {
                        "id": to,
                        "name": to_node['long_name'],
                        "short": to_node['short_name'],
                        "height": 30,
                        "stroke": None,
                        'fill': {"src": utils.graph_icon(to_node['long_name'])}
                    }
                )

        return graph_data

    def store_node(self, data):
        if not data:
            return
        payload = dict(data["decoded"]["json_payload"])
        expected = [
            "hw_model",
            "long_name",
            "short_name",
            "macaddr",
            "public_key",
            "role",
            "firmware_version"
        ]
        for attr in expected:
            if attr not in payload:
                payload[attr] = None
        # Ensure role is set to 0 if missing or None
        if payload["role"] is None:
            payload["role"] = 0

        sql = """INSERT INTO nodeinfo (
    id,
    long_name,
    short_name,
    hw_model,
    role,
    macaddr,
    public_key,
    firmware_version,
    ts_updated
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON DUPLICATE KEY UPDATE
long_name = VALUES(long_name),
short_name = VALUES(short_name),
hw_model = COALESCE(VALUES(hw_model), hw_model),
role = COALESCE(VALUES(role), role),
macaddr = COALESCE(VALUES(macaddr), macaddr),
public_key = COALESCE(VALUES(public_key), public_key),
firmware_version = COALESCE(VALUES(firmware_version), firmware_version),
ts_updated = VALUES(ts_updated)"""
        values = (
            data["from"],
            payload["long_name"],
            payload["short_name"],
            payload["hw_model"],
            payload["role"],
            payload["macaddr"],
            payload["public_key"],
            payload["firmware_version"]
        )
        cur = self.db.cursor()
        cur.execute(sql, values)
        self.db.commit()

    def store_position(self, data, source="position"):
        payload = dict(data["decoded"]["json_payload"])
        expected = [
            "altitude",
            "ground_speed",
            "ground_track",
            "latitude_i",
            "location_source",
            "longitude_i",
            "precision_bits",
            "time"
        ]

        if "position_precision" in payload:
            payload["precision_bits"] = payload["position_precision"]
        for attr in expected:
            if attr not in payload:
                payload[attr] = None
        if payload["latitude_i"] and payload["longitude_i"]:
            self.update_geocode(
                self.verify_node(data["from"]),
                payload["latitude_i"],
                payload["longitude_i"]
            )
        sql = """INSERT INTO position (
    id,
    altitude,
    ground_speed,
    ground_track,
    latitude_i,
    location_source,
    longitude_i,
    precision_bits,
    position_time,
    ts_updated
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(%s), NOW())
ON DUPLICATE KEY UPDATE
altitude = VALUES(altitude),
ground_speed = VALUES(ground_speed),
ground_track = VALUES(ground_track),
latitude_i = VALUES(latitude_i),
location_source = VALUES(location_source),
longitude_i = VALUES(longitude_i),
precision_bits= VALUES(precision_bits),
position_time = VALUES(position_time),
ts_updated = VALUES(ts_updated)"""
        values = (
            self.verify_node(data["from"]),
            payload["altitude"],
            payload["ground_speed"],
            payload["ground_track"],
            payload["latitude_i"],
            payload["location_source"],
            payload["longitude_i"],
            payload["precision_bits"],
            payload["time"] or time.time()
        )
        cur = self.db.cursor()
        cur.execute(sql, values)
        self.log_position(
            data["from"],
            payload["latitude_i"],
            payload["longitude_i"],
            source
        )
        self.db.commit()

        # --- Zápis hop_start do nodeinfo, pokud je v datech ---
        if "hop_start" in data:
            self.update_hop_start(data["from"], data["hop_start"])

    def store_mapreport(self, data):
        self.store_node(data)
        self.store_position(data, "mapreport")

    def store_neighborinfo(self, data):
        node_id = self.verify_node(data["from"])
        payload = dict(data["decoded"]["json_payload"])
        if "neighbors" not in payload:
            return
        sql = "DELETE FROM neighborinfo WHERE id = %s"
        params = (node_id, )
        self.db.cursor().execute(sql, params)
        for neighbor in payload["neighbors"]:
            sql = """INSERT INTO neighborinfo
(id, neighbor_id, snr, ts_created) VALUES (%s, %s, %s, NOW())"""
            params = (
                node_id,
                self.verify_node(neighbor["node_id"]),
                neighbor["snr"] if "snr" in neighbor else None
            )
            self.db.cursor().execute(sql, params)
        self.db.commit()

    def store_traceroute(self, data):
        from_id = self.verify_node(data["from"])
        to_id = self.verify_node(data["to"])
        payload = dict(data["decoded"]["json_payload"])
        route = None
        snr = None
        if "route" in payload:
            route = ";".join(str(r) for r in payload["route"])
        if "snr_towards" in payload:
            snr = ";".join(str(s) for s in payload["snr_towards"])

        sql = """INSERT INTO traceroute
(from_id, to_id, route, snr, ts_created) VALUES (%s, %s, %s, %s, NOW())"""
        params = (
            from_id,
            to_id,
            route,
            snr
        )
        self.db.cursor().execute(sql, params)
        self.db.commit()

    def update_hop_start(self, node_id, hop_start):
        """Aktualizuje hodnotu hop_start v tabulce nodeinfo pro daný node_id."""
        sql = "UPDATE nodeinfo SET hop_start = %s, ts_updated = NOW() WHERE id = %s"
        params = (hop_start, node_id)
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()
        self.db.commit()

    def store_telemetry(self, data):
        cur = self.db.cursor()
        cur.execute(f"SELECT COUNT(*) FROM telemetry")
        count = cur.fetchone()[0]
        if count >= 20000:
            cur.execute(f"""DELETE FROM telemetry
ORDER BY ts_created ASC LIMIT 1""")
        cur.close()
        self.db.commit()

        node_id = self.verify_node(data["from"])
        payload = dict(data["decoded"]["json_payload"])

        data_metrics = {
            "air_util_tx": None,
            "battery_level": None,
            "channel_utilization": None,
            "uptime_seconds": None,
            "voltage": None,
            "temperature": None,
            "relative_humidity": None,
            "barometric_pressure": None,
            "gas_resistance": None,
            "current": None
        }

        metrics = [
            "device_metrics",
            "environment_metrics"
        ]
        for metric in metrics:
            if metric not in payload:
                continue
            for key in data_metrics:
                if key in payload[metric]:
                    data_metrics[key] = payload[metric][key]

        sql = """INSERT INTO telemetry
(id, air_util_tx, battery_level, channel_utilization,
uptime_seconds, voltage, temperature, relative_humidity,
barometric_pressure, gas_resistance, current, telemetry_time)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(%s))
"""
        params = (
            node_id,
            data_metrics["air_util_tx"],
            data_metrics["battery_level"],
            data_metrics["channel_utilization"],
            data_metrics["uptime_seconds"],
            data_metrics["voltage"],
            data_metrics["temperature"],
            data_metrics["relative_humidity"],
            data_metrics["barometric_pressure"],
            data_metrics["gas_resistance"],
            data_metrics["current"],
            payload["time"]
        )
        self.db.cursor().execute(sql, params)
        self.db.commit()

        # --- Zápis hop_start do nodeinfo, pokud je v datech ---
        if "hop_start" in data:
            self.update_hop_start(node_id, data["hop_start"])

    def store_text(self, data):
        from_id = self.verify_node(data["from"])
        to_id = self.verify_node(data["to"],noupdate=True)
        payload = dict(data["decoded"]["json_payload"])
        sql = """INSERT INTO text
(from_id, to_id, text, channel, ts_created)
VALUES (%s, %s, %s, %s, NOW())"""
        params = (
            from_id,
            to_id,
            payload["text"],
            data["channel"] if "channel" in data else 0
        )
        self.db.cursor().execute(sql, params)
        self.db.commit()
        match = re.search(
            r"meshinfo (\d{4})",
            payload["text"].decode(),
            re.IGNORECASE
        )
        if match:
            otp = match.group(1)
            node = from_id
            self.claim_node(node, otp)

    def claim_node(self, node, otp):
        sql = """SELECT email FROM meshuser
WHERE otp = %s"""
        params = (otp, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        owner = row[0] if row else None
        cur.close()
        if not owner:
            return
        sql = """UPDATE meshuser
SET otp = NULL WHERE email = %s
"""
        params = (owner, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()

        sql = """UPDATE nodeinfo
SET owner = %s WHERE id = %s"""
        params = (
            owner,
            node
        )
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()
        self.db.commit()

    def verify_node(self, id, via=None, noupdate=False):
        query = "SELECT 1 FROM nodeinfo where id = %s"
        param = (id, )
        cur = self.db.cursor()
        cur.execute(query, param)
        found = True if cur.fetchone() else False
        cur.close()
        if not found:
            self.store_node(self.unknown(id))
        else:
            if noupdate:
                return id
            if via:
                sql = """UPDATE nodeinfo SET
ts_seen = NOW(), updated_via = %s WHERE id = %s"""
                param = (via, id)
            else:
                sql = "UPDATE nodeinfo SET ts_seen = NOW() WHERE id = %s"
                param = (id, )
            cur = self.db.cursor()
            cur.execute(sql, param)
            cur.close()
        return id

    def log_data(self, topic, data):
        cur = self.db.cursor()
        cur.execute(f"SELECT COUNT(*) FROM meshlog")
        count = cur.fetchone()[0]
        if count >= 2000:
            cur.execute(f"DELETE FROM meshlog ORDER BY ts_created ASC LIMIT 1")
        self.db.commit()

        sql = "INSERT INTO meshlog (topic, message) VALUES (%s, %s)"
        params = (topic, json.dumps(data, indent=4, cls=CustomJSONEncoder))
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()
        self.db.commit()
        logging.debug(json.dumps(data, indent=4, cls=CustomJSONEncoder))

    def log_position(self, id, lat, lon, source):
        if not lat or not lon:
            return
        sql = """DELETE FROM positionlog
WHERE ts_created < NOW() - INTERVAL 1 DAY
AND id = %s"""
        params = (id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()
        self.db.commit()
        moved = True
        sql = """SELECT latitude_i, longitude_i FROM positionlog
WHERE id = %s ORDER BY ts_created DESC LIMIT 1"""
        params = (id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        if row and row[0] == lat and row[1] == lon:
            moved = False
        cur.close()
        if not moved:
            return
        sql = """INSERT INTO positionlog
(id, latitude_i, longitude_i, source) VALUES (%s, %s, %s, %s)"""
        params = (id, lat, lon, source)
        cur = self.db.cursor()
        cur.execute(sql, params)
        cur.close()
        self.db.commit()
        logging.info(f"Position updated for {id}")

    def store(self, data, topic):
        if not data:
            return
        self.log_data(topic, data)
        if "from" in data:
            frm = data["from"]
            via = self.int_id(topic.split("/")[-1])
            self.verify_node(frm, via)
        tp = data["type"]
        if tp == "nodeinfo":
            self.store_node(data)
        elif tp == "position":
            self.store_position(data)
        elif tp == "mapreport":
            self.store_mapreport(data)
        elif tp == "neighborinfo":
            self.store_neighborinfo(data)
        elif tp == "traceroute":
            self.store_traceroute(data)
        elif tp == "telemetry":
            self.store_telemetry(data)
        elif tp == "text":
            self.store_text(data)

    def setup_database(self):
        creates = [
            """CREATE TABLE IF NOT EXISTS meshuser (
    email VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password BINARY(60) NOT NULL,
    verification CHAR(4),
    otp CHAR(4),
    status VARCHAR(12) DEFAULT 'CREATED',
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ts_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (username),
    INDEX idx_meshuser_username (username)
)""",
            """CREATE TABLE IF NOT EXISTS nodeinfo (
    id INT UNSIGNED PRIMARY KEY,
    long_name VARCHAR(40) NOT NULL,
    short_name VARCHAR(5) NOT NULL,
    hw_model INT UNSIGNED,
    role INT UNSIGNED,
    firmware_version VARCHAR(40),
    owner VARCHAR(255),
    updated_via INT UNSIGNED,
    ts_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ts_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner) REFERENCES meshuser(email)
)""",
            """CREATE TABLE IF NOT EXISTS position (
    id INT UNSIGNED PRIMARY KEY,
    altitude INT,
    ground_speed INT,
    ground_track INT,
    latitude_i INT,
    longitude_i INT,
    location_source INT,
    precision_bits INT UNSIGNED,
    position_time TIMESTAMP,
    geocoded VARCHAR(255),
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ts_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""",
            """CREATE TABLE IF NOT EXISTS neighborinfo (
    id INT UNSIGNED,
    neighbor_id INT UNSIGNED,
    snr INT SIGNED,
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, neighbor_id)
)""",
            """CREATE TABLE IF NOT EXISTS traceroute (
    from_id INT UNSIGNED NOT NULL,
    to_id INT UNSIGNED NOT NULL,
    route VARCHAR(255),
    snr VARCHAR(255),
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""",
            """CREATE TABLE IF NOT EXISTS telemetry (
    id INT UNSIGNED NOT NULL,
    air_util_tx FLOAT(10, 7),
    battery_level INT,
    channel_utilization FLOAT(10, 7),
    uptime_seconds INT UNSIGNED,
    voltage FLOAT(10, 7),
    temperature FLOAT(10, 7),
    relative_humidity FLOAT(10, 7),
    barometric_pressure FLOAT(12, 7),
    gas_resistance FLOAT(10, 7),
    current FLOAT(10, 7),
    telemetry_time TIMESTAMP,
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_telemetry_id (id)
)
""",
            """CREATE TABLE IF NOT EXISTS text (
    from_id INT UNSIGNED NOT NULL,
    to_id INT UNSIGNED NOT NULL,
    channel INT UNSIGNED NOT NULL,
    text VARCHAR(255),
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""",
            """CREATE TABLE IF NOT EXISTS  meshlog (
    topic varchar(255) not null,
    message text,
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""",
            """CREATE TABLE IF NOT EXISTS  positionlog (
    id INT UNSIGNED NOT NULL,
    latitude_i INT NOT NULL,
    longitude_i INT NOT NULL,
    source VARCHAR(35) NOT NULL,
    ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, ts_created)
)"""
        ]
        cur = self.db.cursor()
        for create in creates:
            cur.execute(create)
        cur.close()
        self.db.commit()

    def import_nodes(self, filename):
        fh = open(filename, "r")
        j = json.loads(fh.read())
        fh.close()
        records = []
        for node_id in j:
            record = {}
            node = j[node_id]
            int_id = self.int_id(node_id)
            record["id"] = int_id
            record["long_name"] = node["longname"]
            record["short_name"] = node["shortname"]
            record["hw_model"] = node["hardware"]
            record["role"] = node["role"] if "role" in node else 0
            if "mapreport" in node and "firmware_version" in node["mapreport"]:
                record["firmware_version"] = \
                    node["mapreport"]["firmware_version"]
            else:
                record["firmware_version"] = None
            records.append(record)

        for record in records:
            sql = """INSERT INTO nodeinfo (
    id,
    long_name,
    short_name,
    hw_model,
    role,
    firmware_version,
    ts_updated
)
VALUES (%s, %s, %s, %s, %s, %s, NOW())
ON DUPLICATE KEY UPDATE
long_name = VALUES(long_name),
short_name = VALUES(short_name),
hw_model = COALESCE(VALUES(hw_model), hw_model),
role = COALESCE(VALUES(role), role),
firmware_version = COALESCE(VALUES(firmware_version), firmware_version),
ts_updated = VALUES(ts_updated)"""
            values = (
                record["id"],
                record["long_name"],
                record["short_name"],
                record["hw_model"],
                record["role"],
                record["firmware_version"]
            )
            cur = self.db.cursor()
            cur.execute(sql, values)
        self.db.commit()

    def import_chat(self, filename):
        fh = open(filename, "r")
        j = json.loads(fh.read())
        fh.close()
        records = []
        for channel in j["channels"]:
            for message in j["channels"][channel]["messages"]:
                records.append({
                    "from_id": self.int_id(message["from"]),
                    "to_id": self.int_id(message["to"]),
                    "channel": channel,
                    "text": message["text"],
                    "ts_created": message["timestamp"]
                })
        sorted_records = sorted(
            records,
            key=lambda x: x["ts_created"],
            reverse=True
        )
        sql = """INSERT into text (from_id, to_id, channel, text, ts_created)
VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s))
"""
        total = len(sorted_records)
        count = 1
        for record in sorted_records:
            params = (
                record["from_id"],
                record["to_id"],
                record["channel"],
                record["text"],
                record["ts_created"]
            )
            print(f"Writing record {count} of {total} ...")
            count += 1
            try:
                cur = self.db.cursor()
                cur.execute(sql, params)
                cur.close()
            except Exception as e:
                print(f"failed to write record.")
        self.db.commit()

    def get_data_for_qr(self, node_id):
        sql = "SELECT long_name, short_name, macaddr, public_key, hw_model, role FROM nodeinfo WHERE id = %s"
        params = (node_id, )
        cur = self.db.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row:
            macaddr = row[2] if row[2] is not None else b""
            public_key = row[3] if row[3] is not None else b""
            hw_model = row[4] if row[4] is not None else 0
            role = row[5] if row[5] is not None else 0
            debug_data = {
                "id": node_id,
                "hex_id": utils.convert_node_id_from_int_to_hex(int(node_id)),
                "long_name": row[0] or "",
                "short_name": row[1] or "",
                "macaddr": macaddr,
                "public_key": public_key,
                "hw_model": meshtastic_support.HardwareModel(hw_model).name,
                "role": MeshData.role_number_to_string(role)
            }
            #import sys, pprint
            #print("get_data_for_qr:", pprint.pformat(debug_data), file=sys.stderr)
            return debug_data
        return None

    def role_number_to_string(role_num):
        role_map = {
            0: "CLIENT",
            1: "CLIENT_MUTE",
            2: "ROUTER",
            3: "ROUTER_CLIENT",
            4: "REPEATER",
            5: "TRACKER",
            6: "SENSOR",
            7: "TAK",
            8: "CLIENT_HIDDEN",
            9: "LOST_AND_FOUND",
            10: "TAK_TRACKER",
            11: "ROUTER_LATE"
        }
        return role_map.get(int(role_num), "Unknown")


def create_database():
    config = configparser.ConfigParser()
    config.read('config.ini')

    db = mysql.connector.connect(
        host="db",
        user="root",
        password="passw0rd",
    )
    sqls = [
        f"""CREATE DATABASE IF NOT EXISTS {config["database"]["database"]}""",
        f"""CREATE USER IF NOT EXISTS '{config["database"]["username"]}'@'%'
IDENTIFIED BY '{config["database"]["password"]}'""",
        f"""GRANT ALL ON {config["database"]["username"]}.*
TO '$DB_USER'@'%'""",
        f"""ALTER DATABASE {config["database"]["database"]}
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
    ]
    for sql in sqls:
        cur = db.cursor()
        cur.execute(sql)
        cur.close()
    db.commit()


if __name__ == "__main__":
    md = MeshData()
    md.setup_database()