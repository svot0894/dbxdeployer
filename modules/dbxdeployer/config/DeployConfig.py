import dataclasses
from typing import List, Dict, Any

from config.TrackingTable import TrackingTable

@dataclasses.dataclass
class DeployConfig:
    config_version: str | None = None
    root_folder: str | None = None
    dry_run: bool = False
    deployment_order: List[str] = dataclasses.field(default_factory=list)
    
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

    # api endpoints details
    api_configs: Dict[str, dict] = dataclasses.field(default_factory=dict)

    # jinja variables
    vars: Dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def factory(cls, tracking_table: str, **kwargs):

        tracking_table = TrackingTable.from_str(
            table_str=tracking_table
        )

        return cls(
            tracking_table=tracking_table,
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
