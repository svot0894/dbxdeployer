from dataclasses import dataclass
from pathlib import Path
import re


_DEPLOYMENT_PATTERN = re.compile(
    r"^V(?P<version>\d{6})__(?P<description>[a-z0-9_]+)\.sql$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Deployment:
    """
    Immutable representation of a deployment file discovered
    from the 'migrations' directory.
    """
    deployment_id: str
    version: int
    description: str
    file_path: Path

    @property
    def filename(self) -> str:
        return self.file_path.name

    @classmethod
    def from_path(cls, file_path: Path):
        match = _DEPLOYMENT_PATTERN.match(file_path.name)

        if not match:
            raise ValueError(
                f"Invalid deployment filename: {file_path.name}"
            )

        return cls(
            deployment_id = f"V{match.group('version')}",
            version = int(match.group("version")),
            description = match.group("description").replace("_", " "),
            file_path = file_path,
        )