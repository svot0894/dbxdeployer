from dataclasses import dataclass
from enum import Enum

from .deployment import Deployment
from dbxdeployer.domain.deployment_history import DeploymentHistoryEntry


class DeploymentStatus(Enum):
    APPLIED = "APPLIED"
    PENDING = "PENDING"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"
    MISSING_LOCAL_DEPLOYMENT = "MISSING_LOCAL_DEPLOYMENT"

@dataclass(frozen=True)
class PlannedDeployment:
    deployment: Deployment | None
    history_entry: DeploymentHistoryEntry | None
    status: DeploymentStatus

    @property
    def deployment_id(self) -> str:
        if self.deployment is not None:
            return self.deployment.deployment_id
        elif self.history_entry is not None:
            return self.history_entry.deployment_id
        else:
            raise ValueError("Both deployment and history_entry are None, cannot determine deployment_id")

@dataclass(frozen=True)
class DeploymentPlan:
    planned_deployments: tuple[PlannedDeployment, ...]