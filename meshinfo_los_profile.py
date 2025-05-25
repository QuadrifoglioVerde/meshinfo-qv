import json
import utils
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
from scipy.spatial import distance
from geopy.distance import geodesic
import logging
import time
import io
import re
import base64
import hashlib

class LOSProfile():
    def __init__(self, nodes={}, node=None):
        self.nodes = nodes
        self.node = node
        self.terrain_dataset = None  # Dataset pro terén
        self.forest_dataset = None  # Dataset pro lesy

        # Názvy souborů pro terén a lesy
        terrain_file = "srtm_data/terrain_data.tif"
        forest_file = "srtm_data/forest_data.tif"

        # Načtení datasetu terénu
        try:
            if os.path.exists(terrain_file):
                self.terrain_dataset = rasterio.open(terrain_file)
            else:
                logging.warning(f"Terrain file '{terrain_file}' not found.")
        except Exception as e:
            logging.error(f"Error loading terrain file '{terrain_file}': {e}")

        # Načtení datasetu lesů
        try:
            if os.path.exists(forest_file):
                self.forest_dataset = rasterio.open(forest_file)
            else:
                logging.warning(f"Forest file '{forest_file}' not found.")
        except Exception as e:
            logging.error(f"Error loading forest file '{forest_file}': {e}")


    @staticmethod
    def remove_emoji(text):
        emoji_pattern = re.compile(
            "[" 
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002700-\U000027BF"
            u"\U0001F900-\U0001F9FF"
            u"\U00002600-\U000026FF"
            u"\U0001FA70-\U0001FAFF"
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)

    def calculate_distance_between_coords(self, coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        return geodesic((lat1, lon1), (lat2, lon2)).meters

    def read_elevation_from_tif(self, lat, lon):
        """Čtení výšky z datasetu terénu."""
        if not self.terrain_dataset:
            logging.warning("Terrain dataset not loaded.")
            return None
        if self.terrain_dataset.bounds.left <= lon <= self.terrain_dataset.bounds.right and \
           self.terrain_dataset.bounds.bottom <= lat <= self.terrain_dataset.bounds.top:
            row, col = self.terrain_dataset.index(lon, lat)
            elevation = self.terrain_dataset.read(1)[row, col]
            return elevation
        logging.warning(f"No elevation data found for coordinates ({lat}, {lon})")
        return None

    def read_forest_from_tif(self, lat, lon):
        """Zjištění, zda je bod pokryt lesem."""
        if not self.forest_dataset:
            return False  # Pokud dataset neexistuje, žádné lesy nejsou
        if self.forest_dataset.bounds.left <= lon <= self.forest_dataset.bounds.right and \
           self.forest_dataset.bounds.bottom <= lat <= self.forest_dataset.bounds.top:
            row, col = self.forest_dataset.index(lon, lat)
            forest_value = self.forest_dataset.read(1)[row, col]
            return forest_value > 0  # Např. hodnota > 0 znamená les
        return False

    def get_profile_between(self, from_coords, to_coords, resolution=150):
        lat1, lon1 = from_coords["lat"], from_coords["lon"]
        lat2, lon2 = to_coords["lat"], to_coords["lon"]

        lats = np.linspace(lat1, lat2, resolution)
        lons = np.linspace(lon1, lon2, resolution)

        total_distance = self.calculate_distance_between_coords((lat1, lon1), (lat2, lon2))

        # Optimalizace: načti výšky hromadně
        if self.terrain_dataset:
            from rasterio.transform import rowcol
            rows, cols = rowcol(self.terrain_dataset.transform, lons, lats)
            rows = np.clip(rows, 0, self.terrain_dataset.height - 1)
            cols = np.clip(cols, 0, self.terrain_dataset.width - 1)
            elevation_data = self.terrain_dataset.read(1)
            elevations = elevation_data[rows, cols]
        else:
            elevations = np.zeros_like(lats)

        profile = []
        for i, (lat, lon, elev) in enumerate(zip(lats, lons, elevations)):
            distance_along_path = total_distance * (i / (resolution - 1))
            profile.append({
                "lat": lat,
                "lon": lon,
                "distance": round(distance_along_path, 0),  # v metrech
                "elevation": round(elev, 0)            # v metrech
            })
        return profile

    def generate_los_profile(self, coord1, coord2, resolution=150):
        lat1, lon1, alt1 = coord1
        lat2, lon2, alt2 = coord2

        latitudes = np.linspace(lat1, lat2, resolution)
        longitudes = np.linspace(lon1, lon2, resolution)

        # Optimalizace: načti výšky hromadně
        if self.terrain_dataset:
            from rasterio.transform import rowcol
            rows, cols = rowcol(self.terrain_dataset.transform, longitudes, latitudes)
            rows = np.clip(rows, 0, self.terrain_dataset.height - 1)
            cols = np.clip(cols, 0, self.terrain_dataset.width - 1)
            elevation_data = self.terrain_dataset.read(1)
            elevations = elevation_data[rows, cols]
        else:
            elevations = np.zeros_like(latitudes)

        distances = [geodesic((lat1, lon1), (lat, lon)).meters for lat, lon in zip(latitudes, longitudes)]
        profile = [float(elev) for elev in elevations]

        if alt1:
            profile[0] = alt1
        if alt2:
            profile[-1] = alt2

        return distances, profile

    def _get_cache_filename(self, coord1, coord2, label):
        os.makedirs("cache", exist_ok=True)
        hash_input = f"{coord1}-{coord2}-{label}".encode("utf-8")
        filename = hashlib.md5(hash_input).hexdigest() + ".png"
        return os.path.join("cache", filename)

    def plot_los_profile(self, distances, profile, label, dynamic_range=True, coord1=None, coord2=None):
        cache_file = self._get_cache_filename(coord1, coord2, label)

        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")
                return img_base64

        extend_ratio = 0.05
        num_points = len(profile)
        extra_points = int(num_points * extend_ratio)
        total_points = num_points + 2 * extra_points

        extended_distances = np.linspace(-extra_points, num_points + extra_points - 1, total_points)
        extended_distances_km = [(d / (num_points - 1)) * distances[-1] / 1000.0 for d in extended_distances]

        lat1, lon1, alt1 = coord1
        lat2, lon2, alt2 = coord2
        extra_lat_start = lat1 - (lat2 - lat1) * extend_ratio
        extra_lon_start = lon1 - (lon2 - lon1) * extend_ratio
        extra_lat_end = lat2 + (lat2 - lat1) * extend_ratio
        extra_lon_end = lon2 + (lon2 - lon1) * extend_ratio

        lats = np.linspace(extra_lat_start, extra_lat_end, total_points)
        lons = np.linspace(extra_lon_start, extra_lon_end, total_points)

        # --- Optimalizace: vektorové čtení výšek a masky lesa ---
        elevations = np.zeros_like(lats)
        forest_mask = np.zeros_like(lats, dtype=bool)
        if self.terrain_dataset:
            from rasterio.transform import rowcol
            rows, cols = rowcol(self.terrain_dataset.transform, lons, lats)
            rows = np.clip(rows, 0, self.terrain_dataset.height - 1)
            cols = np.clip(cols, 0, self.terrain_dataset.width - 1)
            elevation_data = self.terrain_dataset.read(1)
            elevations = elevation_data[rows, cols]
        if self.forest_dataset:
            from rasterio.transform import rowcol
            rows, cols = rowcol(self.forest_dataset.transform, lons, lats)
            rows = np.clip(rows, 0, self.forest_dataset.height - 1)
            cols = np.clip(cols, 0, self.forest_dataset.width - 1)
            forest_data = self.forest_dataset.read(1)
            forest_mask = forest_data[rows, cols] > 0

        # Vložíme výšky antén na správné pozice
        elevations[extra_points] = alt1
        elevations[-extra_points - 1] = alt2

        # Spojovací čára pouze mezi anténami
        direct_line = np.linspace(alt1, alt2, num_points)

        plt.figure(figsize=(10, 3))
        ax = plt.gca()
        ax.set_facecolor("#f0f4f8")
        plt.margins(x=0, y=0, tight=True)

        all_heights = list(elevations) + list(direct_line)
        min_y = min(all_heights)
        max_y = max(all_heights)

        if dynamic_range:
            padding = (max_y - min_y) * 0.2
            plt.ylim(bottom=max(0, min_y - padding), top=max_y + padding)
        else:
            plt.ylim(bottom=max(0, min_y - 50))

        plt.fill_between(extended_distances_km, elevations, color="#d08770", alpha=0.8, zorder=3, label="Profil terénu")
        plt.plot(extended_distances_km, elevations, color="#a0522d", linewidth=1.5, zorder=4, label="Obrys terénu")

        # Přidání napůl průhledné zelené oblasti na místech lesů
        for i in range(len(elevations) - 1):
            if forest_mask[i]:
                plt.fill_between(
                    [extended_distances_km[i], extended_distances_km[i + 1]],
                    elevations[i] - 1,
                    elevations[i] + 5,
                    color="green",
                    alpha=0.4,
                    edgecolor="none",
                    zorder=1
                )

        main_distances_km = extended_distances_km[extra_points: -extra_points]
        plt.plot(main_distances_km, direct_line, color="#2e8b57", linestyle="dashed", linewidth=2, zorder=5, label="Přímá spojnice")
        plt.scatter([main_distances_km[0], main_distances_km[-1]], [alt1, alt2], color="black", zorder=5)

        clean_label = self.remove_emoji(label)

        plt.xlabel("Vzdálenost (km)")
        plt.ylabel("Nadmořská výška (metry)")
        plt.title(clean_label, fontsize=12, fontweight="bold")

        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
        plt.legend(loc="upper right", fontsize=9)

        plt.savefig(cache_file, format="png", bbox_inches="tight")
        plt.close()

        with open(cache_file, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")
        return img_base64


    def get_profiles(self):
        profiles = {}
        processed_ids = set()  # <== sledujeme už zpracované uzly

        hexid = utils.convert_node_id_from_int_to_hex(self.node)
        if not self.terrain_dataset or hexid not in self.nodes:
            return profiles

        mynode = self.nodes[hexid]
        if "position" not in mynode or "latitude" not in mynode["position"]:
            return profiles

        mylat = mynode["position"]["latitude"]
        mylon = mynode["position"]["longitude"]
        myalt = mynode["position"]["altitude"]

        # 1. Ty slyšíš někoho
        if "neighbors" in mynode:
            for neighbor in mynode["neighbors"]:
                neighbor_id_int = neighbor["neighbor_id"]
                neighbor_id = utils.convert_node_id_from_int_to_hex(neighbor_id_int)

                if neighbor_id in processed_ids or neighbor_id not in self.nodes:
                    continue

                node = self.nodes[neighbor_id]
                if "position" not in node:
                    continue

                lat = node["position"].get("latitude")
                lon = node["position"].get("longitude")
                alt = node["position"].get("altitude")

                if None in (lat, lon, alt) or alt < 0:
                    continue

                dist = self.calculate_distance_between_coords((mylat, mylon), (lat, lon))
                if not dist or not (1000 < dist < 50000):
                    continue

                coord1 = (mylat, mylon, myalt)
                coord2 = (lat, lon, alt)
                lname1 = mynode.get("long_name", "")
                sname1 = mynode.get("short_name", "")
                lname2 = node.get("long_name", "")
                sname2 = node.get("short_name", "")
                label = f"{lname1} ({sname1}) <=> {lname2} ({sname2})"

                # Kontrola, zda obrázek již existuje
                cache_file = self._get_cache_filename(coord1, coord2, label)
                if os.path.exists(cache_file):
                    with open(cache_file, "rb") as f:
                        img_base64 = base64.b64encode(f.read()).decode("utf-8")
                    profiles[neighbor_id] = {
                        "image": img_base64,
                        "distance": dist,
                        "snr": neighbor.get("snr")
                    }
                    processed_ids.add(neighbor_id)
                    continue

                distances, profile = self.generate_los_profile(coord1, coord2)
                image = self.plot_los_profile(distances, profile, label, coord1=coord1, coord2=coord2)

                profiles[neighbor_id] = {
                    "image": image,
                    "distance": dist,
                    "snr": neighbor.get("snr")
                }
                processed_ids.add(neighbor_id)

        # 2. Někdo slyší tebe
        for id, nnode in self.nodes.items():
            if id == hexid or "neighbors" not in nnode or "position" not in nnode:
                continue
            if id in processed_ids:
                continue

            for neighbor in nnode["neighbors"]:
                if neighbor["neighbor_id"] != self.node:
                    continue

                lat = nnode["position"].get("latitude")
                lon = nnode["position"].get("longitude")
                alt = nnode["position"].get("altitude")

                if None in (lat, lon, alt) or alt < 0:
                    continue

                dist = self.calculate_distance_between_coords((mylat, mylon), (lat, lon))
                if not dist or not (1000 < dist < 50000):
                    continue

                coord1 = (mylat, mylon, myalt)
                coord2 = (lat, lon, alt)
                lname1 = mynode.get("long_name", "")
                sname1 = mynode.get("short_name", "")
                lname2 = nnode.get("long_name", "")
                sname2 = nnode.get("short_name", "")
                label = f"{lname1} ({sname1}) <=> {lname2} ({sname2})"

                # Kontrola, zda obrázek již existuje
                cache_file = self._get_cache_filename(coord1, coord2, label)
                if os.path.exists(cache_file):
                    with open(cache_file, "rb") as f:
                        img_base64 = base64.b64encode(f.read()).decode("utf-8")
                    profiles[id] = {
                        "image": img_base64,
                        "distance": dist,
                        "snr": neighbor.get("snr")
                    }
                    processed_ids.add(id)
                    continue

                distances, profile = self.generate_los_profile(coord1, coord2)
                image = self.plot_los_profile(distances, profile, label, coord1=coord1, coord2=coord2)

                profiles[id] = {
                    "image": image,
                    "distance": dist,
                    "snr": neighbor.get("snr")
                }
                processed_ids.add(id)

        return profiles

    def find_highest_point(self, lat, lon, perimeter_m=5000):
        if not self.terrain_dataset:
            return None
        from rasterio.transform import rowcol
        deg_per_m = 1.0 / 111320.0
        step_m = max(5, perimeter_m // 100)
        dists = np.arange(-perimeter_m, perimeter_m + step_m, step_m)
        grid_dlat, grid_dlon = np.meshgrid(dists, dists)
        grid_dist = np.sqrt(grid_dlat**2 + grid_dlon**2)
        mask = grid_dist <= perimeter_m
        lats = lat + grid_dlat * deg_per_m
        lons = lon + grid_dlon * deg_per_m
        lats_masked = lats[mask]
        lons_masked = lons[mask]
        rows, cols = rowcol(self.terrain_dataset.transform, lons_masked, lats_masked)
        rows = np.clip(rows, 0, self.terrain_dataset.height - 1)
        cols = np.clip(cols, 0, self.terrain_dataset.width - 1)
        elevation_data = self.terrain_dataset.read(1)
        elevations = elevation_data[rows, cols]
        if elevations.size == 0:
            return []
        coords = np.column_stack((lats_masked, lons_masked))
        idxs_sorted = np.argsort(-elevations)
        result = []
        used = np.zeros(elevations.shape, dtype=bool)
        elevations_used = set()
        for idx in idxs_sorted:
            this_lat = float(lats_masked[idx])
            this_lon = float(lons_masked[idx])
            this_elev = float(elevations[idx])
            # Přeskoč, pokud už elevation byl použit
            if this_elev in elevations_used:
                continue
            this_coord = (this_lat, this_lon)
            if len(result) == 0:
                result.append({'lat': this_lat, 'lon': this_lon, 'elevation': this_elev})
                used[idx] = True
                elevations_used.add(this_elev)
            else:
                # Vektorově spočítat vzdálenosti ke všem už vybraným bodům
                prev_coords = np.array([[pt['lat'], pt['lon']] for pt in result])
                dists = np.array([geodesic((this_lat, this_lon), (lat2, lon2)).meters for lat2, lon2 in prev_coords])
                if np.all(dists >= 100):
                    result.append({'lat': this_lat, 'lon': this_lon, 'elevation': this_elev})
                    used[idx] = True
                    elevations_used.add(this_elev)
            if len(result) == 3:
                break
        return result


if __name__ == "__main__":
    from meshdata import MeshData
    #md = MeshData()
    #nodes = md.get_nodes()
    #lp = LOSProfile(nodes, 2193198973)
    #print(lp.get_profiles())
