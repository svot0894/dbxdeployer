import structlog
import requests
from collections import defaultdict
from modules.dbxdeployer.config.TrackingTable import TrackingTable

class DatabricksSession:
    workspace_url: str
    warehouse_id: str
    token: str
    tracking_table: TrackingTable

    def __init__(self, workspace_url, warehouse_id, token, logger, tracking_table: TrackingTable):
        self.workspace_url = workspace_url
        self.warehouse_id = warehouse_id
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self.logger = logger
        self.tracking_table = tracking_table


    def execute_sql(self, query: str, logger: structlog.BoundLogger):
        """Executes a SQL query using Databricks SQL API."""
        logger.debug(
            "Executing query"
            , query = query
        )
        try:
            endpoint = f"{self.workspace_url}/api/2.0/sql/statements"
            payload = {
                "statement": query
                , "warehouse_id": self.warehouse_id
            }
            response = requests.post(endpoint, json=payload, headers=self.headers)

            if response.status_code != 200:
                raise Exception(f"Failed to execute query: {response.text}")
            
            return response.json()

        except Exception as e:
            raise e

    def fetch_tracking_metadata():
        pass

    def create_tracking_schema(self, dry_run: bool):
        """Create schema for tracking table if it doesn't exist."""
        query = f"""
            CREATE SCHEMA IF NOT EXISTS {self.tracking_table.fully_qualified_schema_name}
        """
        if dry_run:
            self.logger.debug(
                "Running in dry-run mode. Skipping execution."
                , query = query
            )
        else:
            self.execute_sql(query, logger=self.logger)

    def tracking_schema_exists(self) -> bool:
        """Checks if schema for tracking table exists or not."""
        query = f"""
            SELECT COUNT(1)
            FROM {self.tracking_table.database_name}.INFORMATION_SCHEMA.SCHEMATA
            WHERE
                SCHEMA_NAME = REPLACE('{self.tracking_table.schema_name}','\"','')
        """
        
        result = self.execute_sql(query, logger=self.logger)

        for row in result.result.data_array:
            return row[0] > 0

    def create_tracking_table(self, dry_run: bool) -> None:
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.tracking_table.fully_qualified} (
                VERSION VARCHAR,
                DESCRIPTION VARCHAR,
                SCRIPT VARCHAR,
                SCRIPT_TYPE VARCHAR,
                SCRIPT_OBJECT VARCHAR,
                CHECKSUM VARCHAR,
                EXECUTION_TIME NUMBER,
                STATUS VARCHAR,
                INSTALLED_BY VARCHAR,
                INSTALLED_ON TIMESTAMP
            )
        """
    
        if dry_run:
            self.logger.debug(
                "Running in dry-run mode. Skipping execution."
                , query = query
            )
        else:
            self.execute_sql(query=query, logger=self.logger)
            self.logger.info(
                f"Created tracking table {self.tracking_table.fully_qualified}"
            )

    def tracking_table_exists(self, create_tracking_table: bool, dry_run: bool) -> bool:
        """Check if tracking table exists."""
        

    def api_scripts_metadata(self):
        """Fetch info about all API scripts that have been previously run."""
        query = f"""
            SELECT VERSION, SCRIPT, SCRIPT_OBJECT, CHECKSUM
            FROM {self.tracking_table.fully_qualified}
            WHERE SCRIPT_TYPE = 'A'
            ORDER BY SCRIPT_OBJECT, INSTALLED_ON DESC
        """
        results = self.execute_sql(query, logger=self.logger)

        # parse the results
        sql_scripts = []
        for row in results.result.data_array:
            version, script, script_object, checksum = row
            sql_scripts.append({
            "version": version,
            "script": script,
            "script_object": script_object,
            "checksum": checksum
        })

        # determine max version per object
        max_versions = {}
        for entry in sql_scripts:
            script_object = entry["script_object"]
            version = entry["version"]
            if script_object not in max_versions or version > max_versions[script_object]:
                max_versions[script_object] = version
        
        return sql_scripts, max_versions


    def sql_scripts_metadata(self):
        """Fetch info about all SQL scripts that have been previously run."""
        query = f"""
            SELECT VERSION, SCRIPT, SCRIPT_OBJECT, CHECKSUM
            FROM {self.tracking_table.fully_qualified}
            WHERE SCRIPT_TYPE = 'S'
            ORDER BY SCRIPT_OBJECT, INSTALLED_ON DESC
        """
        results = self.execute_sql(query, logger=self.logger)

        # parse the results
        sql_scripts = []
        for row in results.result.data_array:
            version, script, script_object, checksum = row
            sql_scripts.append({
            "version": version,
            "script": script,
            "script_object": script_object,
            "checksum": checksum
        })

        # determine max version per object
        max_versions = {}
        for entry in sql_scripts:
            script_object = entry["script_object"]
            version = entry["version"]
            if script_object not in max_versions or version > max_versions[script_object]:
                max_versions[script_object] = version
        
        return sql_scripts, max_versions

    def apply_create_script(self, script):
        pass

    def apply_update_script(self, script):
        pass

    def apply_delete_script(self, script):
        pass

    def reset_session():
        pass

    def reset_query_tag():
        pass

    def apply_change_script():
        pass