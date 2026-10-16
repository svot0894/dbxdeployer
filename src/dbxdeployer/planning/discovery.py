# recursively scan 'migrations' folder
# load deployment files
# parse deployment files
# detect duplicate deployments IDs
# sort by version
# return ordered deployments list

from pathlib import Path
from collections import Counter
from ..domain.deployment import Deployment


def discover_deployments(migrations_dir: Path) -> list[Deployment]:
    """Discover, validate, and order deployment files."""

    all_deployments: list[Deployment] = []

    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    for file_path in migrations_dir.rglob("*.sql"):
        try:
            deployment = Deployment.from_path(file_path)
            all_deployments.append(deployment)
        except ValueError as e:
            raise ValueError(
                f"Invalid deployment file discovered: {file_path.name}"
            ) from e

    # Detect duplicate deployment IDs
    deployment_ids = [d.deployment_id for d in all_deployments]
    if len(deployment_ids) != len(set(deployment_ids)):
        duplicates = [
            deployment_id
            for deployment_id, count in Counter(deployment_ids).items()
            if count > 1
        ]
        raise ValueError(f"Duplicate deployment IDs found: {', '.join(duplicates)}")

    # Sort deployments by version
    all_deployments.sort(key=lambda x: x.version)

    return all_deployments