import os
import argparse
from pathlib import Path
import yaml
from modules.dbxdeployer.deploy import deploy

def main():
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

    # creat path to configs.py file
    config_path = os.path.join(root_dir, "configs", args.env, "configs.yml")

    # load configurations
    with open(config_path) as cfg:
        configs = yaml.safe_load(cfg)

    deploy(configs)


if __name__ == "__main__":
    main()
