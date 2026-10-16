from pathlib import Path
import yaml
import structlog

from utils.parse_cli_args import parse_cli_args
from utils.get_yaml_config_kwargs import get_yaml_config_kwargs
from config.DeployConfig import DeployConfig

def load_yaml_config(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"YAML config file not found: {path}.")
    with path.open() as f:
        return yaml.safe_load(f)


def get_merged_config(logger: structlog.BoundLogger):

    # load CLI arguments
    args = parse_cli_args()

    # define config paths using config_folder argument
    config_folder = Path(args.config_folder)

    config_path = config_folder / args.env / "configs.yml"

    # fetch kwargs
    config_kwargs = get_yaml_config_kwargs(
        file_path=config_path
    )

    kwargs = {
        **{k: v for k, v in config_kwargs.items() if v is not None},
    }

    return DeployConfig.factory(**kwargs)