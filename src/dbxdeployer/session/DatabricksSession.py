import hashlib
import time
import structlog
import requests
from utils.format_endpoint import format_endpoint
from session.script import SqlScript
from config.TrackingTable import TrackingTable

class DatabricksSession:
    workspace_url: str
    warehouse_id: str
    token: str
    tracking_table: TrackingTable

    """DatabricksSession class to manage connections and operations with Databricks SQL API."""

    def __init__(
            self,
            workspace_url: str,
            warehouse_id: str,
            user: str,
            token: str,
            logger,
            tracking_table: TrackingTable
        ):
        self.workspace_url = workspace_url
        self.warehouse_id = warehouse_id
        self.user = user
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self.logger = logger
        self.tracking_table = tracking_table

    def execute_sql(self, query: str, logger: structlog.BoundLogger):
        """Executes a SQL query using Databricks SQL API."""

        logger.debug("Executing query...", query = query)
        endpoint = f"{self.workspace_url}/api/2.0/sql/statements"
        payload = {
            "statement": query
            , "warehouse_id": self.warehouse_id
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, verify=False)

            if response.status_code != 200:
                raise Exception(f"Failed to execute query: {response.text}")

            response_json = response.json()
            sql_statement_id = response_json.get("statement_id")

            expected_final_status = ['SUCCEEDED', 'FAILED']

            # if query execution takes more than 10 seconds (default), we need to poll the status
            while response_json.get("status").get("state") not in expected_final_status:
                time.sleep(5)
                response_json = requests.get(
                    endpoint + f"/{sql_statement_id}",
                    headers=self.headers,
                    verify=False
                ).json()

            if response_json.get("status").get("state") == "FAILED":
                error_message = response_json.get("status").get("error").get("message")
                raise Exception(f"Failed to execute query due to a syntax error: {error_message}")
            
            return response_json

        except Exception as e:
            raise e

    def fetch_tracking_table_metadata(self):
        """Check query metadata about tracking table creation."""
        query = f"""\
            SELECT
                CREATED,
                LAST_ALTERED
            FROM {self.tracking_table.database_name}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = REPLACE('{self.tracking_table.schema_name}','\"','')
                AND TABLE_NAME = REPLACE('{self.tracking_table.table_name}','\"','')
        """
        results = self.execute_sql(query=query, logger=self.logger)

        # If there are no results, the tracking table does not exist
        tracking_table_metadata = dict()

        if results.get("result", {}).get("data_array"):
            row = results["result"]["data_array"][0]
            tracking_table_metadata = {
            "created": row[0],
            "last_altered": row[1]
            }

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

        # If there are no results, the schema does not exist
        for row in result.get("result", {}).get("data_array"):
            schema_exists = int(row[0]) > 0
        
        return schema_exists

    def create_tracking_table(self, dry_run: bool) -> None:
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.tracking_table.fully_qualified} (
                VERSION STRING,
                DESCRIPTION STRING,
                SCRIPT STRING,
                SCRIPT_TYPE STRING,
                SCRIPT_OBJECT STRING,
                SCRIPT_OPERATION STRING,
                CHECKSUM STRING,
                EXECUTION_TIME INT,
                STATUS STRING,
                INSTALLED_BY STRING,
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

    def get_scripts_metadata(self, script_type: str, create_tracking_table: bool, dry_run: bool) -> dict:
        """Fetch max version per object for API scripts that have been previously run."""

        tracking_table_exists = self.tracking_table_exists(
            create_tracking_table=create_tracking_table,
            dry_run=dry_run
        )

        if not tracking_table_exists:
            return None, None

        query = f"""
            SELECT SCRIPT_OBJECT, MAX(VERSION) AS MAX_VERSION
            FROM {self.tracking_table.fully_qualified}
            WHERE SCRIPT_TYPE = '{script_type}' AND STATUS = 'Success'
            GROUP BY SCRIPT_OBJECT
        """
        results = self.execute_sql(query, logger=self.logger)

        # determine max version per object
        max_versions = {}
        for row in results.get("result", {}).get("data_array", []):
            script_object, max_version = row
            if script_object not in max_versions or max_version > max_versions[script_object]:
                max_versions[script_object] = max_version
        
        self.logger.info(
            f"Max applied '{script_type}' script version per object %(max_versions)s"
            % {"max_versions": max_versions}
        )
        
        return max_versions

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
        
        logger.info("Applying change script...")

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
            INSERT INTO {self.tracking_table.fully_qualified} (
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