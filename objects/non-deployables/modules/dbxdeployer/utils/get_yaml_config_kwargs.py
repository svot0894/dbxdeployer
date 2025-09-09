from pathlib import Path
import yaml


def load_yaml_config(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"YAML config file not found: {path}.")
    with path.open() as f:
        return yaml.safe_load(f)


def get_yaml_config_kwargs(file_path: Path):
    """Load YAML inputs."""

    kwargs = {
        k.replace("-", "_"): v for (k, v) in load_yaml_config(file_path).items()
    }

    return {k: v for k, v in kwargs.items() if v is not None}