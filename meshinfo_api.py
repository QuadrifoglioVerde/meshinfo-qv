from flask import Flask, request, jsonify
import configparser
import logging
import utils
from meshdata import MeshData
from meshinfo_los_profile import LOSProfile
from paste.translogger import TransLogger
from waitress import serve
import json
import io
import base64
import qrcode
from flask import send_file
from meshtastic_custom import admin_pb2, mesh_pb2

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")


@app.route('/api/node_activity', methods=['GET'])
def node_activity():
    md = MeshData()
    activity = md.get_node_activity()
    return jsonify(activity)


@app.route('/api/chat', methods=['GET'])
def api_chat():
    try:
        md = MeshData()
        nodes = md.get_nodes(with_neighbors=False, with_position=False)
        chat = md.get_chat()
        chat_data = []
        for message in chat:
            chat_entry = {
                "ts_created": message["ts_created"],
                "from": message["from"],
                "text": message["text"]
            }
            if message["from"] in nodes:
                chat_entry["short_name"] = nodes[message["from"]]["short_name"]
                chat_entry["from_name"] = nodes[message["from"]]["long_name"] + " (" + nodes[message["from"]]["short_name"] + ")"
                chat_entry["from_link"] = f"node_{message['from']}.html"
            chat_data.append(chat_entry)
        return jsonify(chat_data)
    except Exception as e:
        app.logger.error(f"Chyba v /api/chat: {e}")
        return jsonify({"error": "Došlo k chybě na serveru"}), 500


@app.route('/api/terrain', methods=['GET'])
def terrain_profile():
    try:
        from_lat = request.args.get("from_lat", type=float)
        from_lon = request.args.get("from_lon", type=float)
        to_lat = request.args.get("to_lat", type=float)
        to_lon = request.args.get("to_lon", type=float)
        if None in (from_lat, from_lon, to_lat, to_lon):
            return jsonify({"error": "Musíte zadat parametry from_lat, from_lon, to_lat, to_lon"}), 400
        from_coords = {"lat": from_lat, "lon": from_lon}
        to_coords = {"lat": to_lat, "lon": to_lon}
        los = LOSProfile()
        profile = los.get_profile_between(from_coords, to_coords)
        return app.response_class(
            response=json.dumps(profile, cls=NumpyEncoder),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        app.logger.error(f"Chyba v /api/terrain-profile: {e}")
        return jsonify({"error": "Interní chyba serveru"}), 500


@app.route('/api/highest_point', methods=['GET'])
def api_highest_point():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        perimeter = request.args.get('perimeter', default=5000, type=int)
        if lat is None or lon is None:
            return jsonify({'error': 'Chybí parametr lat nebo lon'}), 400
        los = LOSProfile()
        result = los.find_highest_point(lat, lon, perimeter)
        if result and isinstance(result, list) and len(result) > 0:
            return jsonify(result)
        else:
            return jsonify({'error': 'Nebylo nalezeno žádné místo'}), 404
    except Exception as e:
        app.logger.error(f"Chyba v /api/highest_point: {e}")
        return jsonify({'error': 'Interní chyba serveru'}), 500


@app.route('/api/elevation', methods=['GET'])
def api_elevation():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        if lat is None or lon is None:
            return jsonify({'error': 'Chybí parametr lat nebo lon'}), 400
        los = LOSProfile()
        elevation = los.read_elevation_from_tif(lat, lon)
        if elevation is None:
            return jsonify({'error': 'Nebylo nalezeno žádné místo'}), 404
        return jsonify({'lat': float(lat), 'lon': float(lon), 'elevation': float(elevation)})
    except Exception as e:
        app.logger.error(f"Chyba v /api/elevation: {e}")
        return jsonify({'error': 'Interní chyba serveru'}), 500


@app.route('/api/logs', methods=['GET'])
def api_logs():
    try:
        md = MeshData()
        logs = md.get_logs()
        return jsonify(logs)
    except Exception as e:
        app.logger.error(f"Chyba v /api/logs: {e}")
        return jsonify({'error': 'Interní chyba serveru'}), 500


@app.route('/api/qr', methods=['GET'])
def api_qr():
    try:
        node_id = request.args.get('id')
        if not node_id:
            return jsonify({'error': 'Chybí parametr id'}), 400

        md = MeshData()
        node = md.get_data_for_qr(node_id)
        if not node:
            return jsonify({'error': 'Node nenalezen'}), 404

        user = mesh_pb2.User(
            id=("!" + node.get('hex_id', '')),
            short_name=node.get('short_name', ''),
            long_name=node.get('long_name', ''),
            macaddr=base64.b64decode(node.get('macaddr', b'')),
            hw_model=node.get('hw_model', ''),
            role=node.get('role', ''),
            public_key=base64.b64decode(node.get('public_key', b''))
        )

        contact = admin_pb2.SharedContact(
            node_num=int(node_id),
            user=user
        )

        contact_bytes = contact.SerializeToString()
        b64 = base64.urlsafe_b64encode(contact_bytes).decode('utf-8').rstrip('=')
        url = f"https://meshtastic.org/v/#{b64}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Chyba v /api/qr: {e}")
        return jsonify({'error': 'Interní chyba serveru'}), 500


def run():
    # Enable Waitress logging
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = int(config["webserver"]["api"])

    waitress_logger = logging.getLogger("waitress")
    waitress_logger.setLevel(logging.DEBUG)  # Enable all logs from Waitress
    #  serve(app, host="0.0.0.0", port=port)
    serve(
        TransLogger(
            app,
            setup_console_handler=False,
            logger=waitress_logger
        ),
        port=port
    )


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = int(config["webserver"]["api"])
    app.run(debug=True, port=port)
