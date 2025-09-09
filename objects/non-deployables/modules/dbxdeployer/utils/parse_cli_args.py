import argparse


def parse_cli_args():
    """Function used to parse command-line arguments for the dbxdeployer module."""
    parser = argparse.ArgumentParser(
        description="Load environment-specific configurations."
    )
    parser.add_argument(
        "--env",
        choices=["dev", "tst", "stg", "prd"],
        required=True,
        type=str,
        help="The environment to load configurations for (e.g. dev, tst, stg, prd)."
    )
    parser.add_argument(
        "--config_folder",
        type=str,
        help="Path to the folder where configs.yml and api-configs.yml files are located."
    )
    args = parser.parse_args()
    return args