import dataclasses
from typing import List
import structlog
import logging

from config.TrackingTable import TrackingTable

logger = structlog.get_logger(__name__)

@dataclasses.dataclass
class DeployConfig:
    config_version: str | None = None
    root_folder: str | None = None
    dry_run: bool = False
    deployment_order: List[str] = dataclasses.field(default_factory=list)
    log_level: int = logging.INFO
    
    # tracking table variables
    tracking_table: TrackingTable | None = dataclasses.field(
        default_factory=TrackingTable
    )
    create_tracking_table: bool = False

    # session variables
    workspace_url: str | None = None
    warehouse_id: str | None = None
    user: str | None = None
    token: str | None = None

    # jinja variables
    vars: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def factory(
        cls,
        tracking_table: str,
        log_level: int = logging.INFO,
        **kwargs
    ):

        tracking_table = TrackingTable.from_str(
            table_str=tracking_table
        )

        return cls(
            tracking_table=tracking_table,
            log_level=log_level,
            **kwargs
        )

    def get_session_kwargs(self) -> dict:
        """Prepares variables for Databricks session instance."""

        session_kwargs = {
            "workspace_url": self.workspace_url,
            "warehouse_id": self.warehouse_id,
            "user": self.user,
            "token": self.token,
            "tracking_table": self.tracking_table,
        }

        return {k: v for k, v in session_kwargs.items() if v is not None}

    def log_details(self):
        logger.info("Using root folder", root_folder=str(self.root_folder))
        logger.info("Using variables", vars=self.vars)