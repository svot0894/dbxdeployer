import dataclasses
from typing import ClassVar

@dataclasses.dataclass
class TrackingTable:
    _default_database_name: ClassVar[str] = "METADATA"
    _default_schema_name: ClassVar[str] = "DBXDEPLOYER_SCH"
    _default_table_name: ClassVar[str] = "DBX_DEPLOYER_TRACKING_TABLE"

    table_name: str = "DBX_DEPLOYER_TRACKING_TABLE"
    schema_name: str = "DBXDEPLOYER_SCH"
    database_name: str = "METADATA"

    @property
    def fully_qualified(self) -> str:
        return f"{self.database_name}.{self.schema_name}.{self.table_name}"

    @property
    def fully_qualified_schema_name(self) -> str:
        return f"{self.database_name}.{self.schema_name}"