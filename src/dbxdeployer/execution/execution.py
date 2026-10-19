# Contains ExecutionStatus and DeploymentExecution classes

from datetime import datetime
from dataclasses import dataclass
from enum import StrEnum


class ExecutionStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class DeploymentExecution:
    deployment_id: str
    execution_id: str
    run_id: str
    version: int
    checksum: str
    deployed_by: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None

    @property
    def duration_ms(self) -> int | None:
        """Returns the duration of the execution in milliseconds."""
        if self.completed_at is None:
            return None
        return int((self.completed_at - self.started_at).total_seconds() * 1000)
        