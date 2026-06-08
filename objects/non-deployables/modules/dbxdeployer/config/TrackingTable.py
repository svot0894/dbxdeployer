import dataclasses
from typing import ClassVar

@dataclasses.dataclass
class TrackingTable:
    _default_database_name: ClassVar[str] = "DB_NAME"
    _default_schema_name: ClassVar[str] = "DBXDEPLOYER_SCH"
    _default_table_name: ClassVar[str] = "DBX_DEPLOYER_TRACKING_TABLE"

    table_name: str = "DBX_DEPLOYER_TRACKING_TABLE"
    schema_name: str = "DBXDEPLOYER_SCH"
    database_name: str = "DB_NAME"

    @property
    def fully_qualified(self) -> str:
        return f"{self.database_name}.{self.schema_name}.{self.table_name}"

    @property
    def fully_qualified_schema_name(self) -> str:
        return f"{self.database_name}.{self.schema_name}"
    
    @classmethod
    def from_str(cls, table_str: str):
        database_name = cls._default_database_name
        schema_name = cls._default_schema_name
        table_name = cls._default_table_name

        if table_str is not None:
            table_name_parts = table_str.strip().split(".")
            if len(table_name_parts) == 1:
                table_name = table_name_parts[0]
            elif len(table_name_parts) == 2:
                table_name = table_name_parts[1]
                schema_name = table_name_parts[0]
            elif len(table_name_parts) == 3:
                table_name = table_name_parts[2]
                schema_name = table_name_parts[1]
                database_name = table_name_parts[0]
            else:
                raise ValueError(f"Invalid tracking table name: {table_str}")

        return cls(
            table_name=table_name,
            schema_name=schema_name,
            database_name=database_name
        )