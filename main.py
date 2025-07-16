import os
import argparse
from pathlib import Path
import yaml
import structlog
from modules.dbxdeployer.session.DatabricksSession import DatabricksSession
from modules.dbxdeployer.deploy import deploy

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
        "env"
        , type=str
        , help="The environment to load configurations for (e.g. dev, tst, stg, prd)."
    )
    args = parser.parse_args()

    # define root directory
    root_dir = Path(__file__).parent

    # creat path to configs.yml file
    config_path = os.path.join(root_dir, "configs", args.env, "configs.yml")

    # create path to api-configs.yml file
    api_config_paths = os.path.join(root_dir, "configs", "api-configs.yml")

    # load environmental configs.yml and api-configs.yml
    configs = load_yaml_config(config_path)
    api_configs = load_yaml_config(api_config_paths)
    
    # initiate Databricks session
    session = DatabricksSession(
        workspace_url=configs["workspace_url"],
        warehouse_id=configs["warehouse_id"],
        token=configs["token"],
        logger=logger,
        tracking_table=configs["tracking_table"]
    )

    deploy(configs, api_configs, session)


if __name__ == "__main__":
    main()
