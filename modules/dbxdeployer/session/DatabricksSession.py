import hashlib
import time
import structlog
import requests
from collections import defaultdict
from modules.dbxdeployer.script import SqlScript
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

    def fetch_tracking_table_metadata(self):
        """Check query metadata about tracking table creation."""
        query = f"""\
            SELECT
                CREATED,
                LAST_ALTERED
            FROM {self.change_history_table.database_name}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = REPLACE('{self.change_history_table.schema_name}','\"','')
                AND TABLE_NAME = REPLACE('{self.change_history_table.table_name}','\"','')
        """
        results = self.execute_sql(query=query, logger=self.logger)

        # Collect all the results into a list
        tracking_table_metadata = dict()
        for row in results.result.data_array:
            tracking_table_metadata["created"] = row[0]
            tracking_table_metadata["last_altered"] = row[1]

        return tracking_table_metadata

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

        tracking_table_metadata = self.fetch_tracking_table_metadata()

        if tracking_table_metadata:
            self.logger.info(
                f"Using existing tracking table {self.tracking_table.fully_qualified}",
                last_altered = tracking_table_metadata["last_altered"]
            )
            return True

        elif create_tracking_table:
            schema_exists = self.tracking_schema_exists()
            if not schema_exists:
                self.create_tracking_schema(dry_run=dry_run)

            self.create_tracking_table(dry_run=dry_run)

            if dry_run:
                return False

            self.logger.info("Created tracking table.")
            return True
        else:
            raise ValueError(
                f"Unable to find tracking table {self.tracking_table.fully_qualified}"
            )
        
        

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

    def apply_api_script(self, script_object, operation, script, api_details):
        """Function used to execute API calls."""

        # Get the API details from the config file
        endpoint = api_details["endpoint"]
        method = api_details["method"]
        requires_body = api_details.get("requires_body", False)
        body_variables = api_details.get("body_variables", None)

        url = f"{self.workspace_url}{endpoint}"

        if method == "POST":
            response = requests.post(url, headers=self.headers, json=script if requires_body else None)
        elif method == "DELETE":
            response = requests.delete(url, headers=self.headers)
        elif method == "PATCH":
            response = requests.patch(url, headers=self.headers, json=script if requires_body else None)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


    def apply_change_script(
            self,
            script: SqlScript,
            script_content: str,
            dry_run: bool,
            logger: structlog.BoundLogger
        ) -> None:
        """Function used to execute SQL scripts."""
        if dry_run:
            logger.debug("Running in dry-run mode. Skipping execution.")
            return
        
        logger.info("Applying change script.")

        # create change-related variables
        checksum = hashlib.sha224(script_content.encode("utf-8")).hexdigest()
        execution_time = 0
        status = "Success"

        # valid and execute script
        if len(script_content) > 0:
            start = time.time()

            try:
                self.execute_sql(query=script_content, logger=logger)
            except Exception as e:
                raise Exception(f"Failed to execute {script.name}") from e

            end = time.time()
            execution_time = round(end - start)

        # Log the execution in the tracking table
        query = f"""\
            INSERT INTO {self.change_history_table.fully_qualified} (
                VERSION,
                DESCRIPTION,
                SCRIPT,
                SCRIPT_TYPE,
                SCRIPT_OBJECT,
                CHECKSUM,
                EXECUTION_TIME,
                STATUS,
                INSTALLED_BY,
                INSTALLED_ON
            ) VALUES (
                '{getattr(script, "version", "")}',
                '{script.description}',
                '{script.name}',
                '{script.type}',
                '{script.object}',
                '{checksum}',
                {execution_time},
                '{status}',
                '{self.user}',
                CURRENT_TIMESTAMP
            );
        """
        self.execute_sql(query=query, logger=logger)