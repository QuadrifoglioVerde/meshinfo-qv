import os
import logging
import utils
from meshdata import MeshData
from meshinfo_los_profile import LOSProfile

def run_cron_job():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LOS")

    logger.info("Fetching nodes from MeshData...")
    md = MeshData()

    logger.info("Cleaning up old nodes...")
    md.cleanup_nodes()

    logger.info("Fetching active nodes...")
    nodes = md.get_nodes(active=True)

    if not nodes:
        logger.error("No nodes found. Exiting.")
        return

    logger.info(f"Found {len(nodes)} nodes. Generating profiles...")

    for node_id in nodes.keys():
        try:
            logger.info(f"Processing node {node_id}...")
            los_profile = LOSProfile(nodes, utils.convert_node_id_from_hex_to_int(node_id))
            profiles = los_profile.get_profiles()

            if profiles:
                logger.info(f"Generated {len(profiles)} profiles for node {node_id}.")
        except Exception as e:
            logger.error(f"Error processing node {node_id}: {e}")

    logger.info("Profile generation completed.")

if __name__ == "__main__":
    run_cron_job()
