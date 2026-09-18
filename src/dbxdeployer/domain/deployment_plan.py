from dataclasses import dataclass
from enum import Enum

from .deployment import Deployment


class DeploymentStatus(Enum):
    APPLIED = "APPLIED"
    PENDING = "PENDING"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"

@dataclass(frozen=True)
class PlannedDeployment:
    deployment: Deployment
    status: DeploymentStatus

@dataclass(frozen=True)
class DeploymentPlan:
    planned_deployments: list[PlannedDeployment]