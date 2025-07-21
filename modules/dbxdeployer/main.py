import argparse
from pathlib import Path
import yaml
import structlog
from config.TrackingTable import TrackingTable
from session.DatabricksSession import DatabricksSession
from deploy import deploy

module_logger = structlog.get_logger(__name__)

def load_yaml_config(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"YAML config file not found: {path}.")
    with path.open() as f:
        return yaml.safe_load(f)

def main():
    logger = structlog.get_logger()

    # parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Load environment-specific configurations."
    )
    parser.add_argument(
        "--env",
        type=str,
        help="The environment to load configurations for (e.g. dev, tst, stg, prd)."
    )
    parser.add_argument(
        "--config_folder",
        type=str,
        help="Path to the folder where configs.yml and api-configs.yml files are located."
    )
    args = parser.parse_args()

    # define config paths using config_folder argument
    config_folder = Path(args.config_folder)
    config_path = config_folder / args.env / "configs.yml"
    api_config_path = config_folder / "api-configs.yml"

    # load configs
    logger.info(f"Loading configs from...")
    configs = load_yaml_config(config_path)
    api_configs = load_yaml_config(api_config_path)

    # merge configs and api_configs
    merged_config = {**configs, **api_configs}

    # initiate Databricks session
    session = DatabricksSession(
        workspace_url=merged_config["workspace_url"],
        warehouse_id=merged_config["warehouse_id"],
        user=merged_config["user"],
        token=merged_config["token"],
        logger=logger,
        tracking_table=TrackingTable.from_str(merged_config["tracking_table"])
    )

    deploy(merged_config, session)

if __name__ == "__main__":
    main()
