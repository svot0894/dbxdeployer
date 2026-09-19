# keeps a history of deployments, including their status and any relevant metadata.
# This can be useful for auditing, troubleshooting, and tracking the progress of deployments over time.

from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentHistoryEntry:
    deployment_id: str
    version: int
    checksum: str