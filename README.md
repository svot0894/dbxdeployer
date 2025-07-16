### Folder Descriptions

- deployables/:
    - Contains all deployable assets.
        - sql-scripts/:
            - Organized by Unity Catalog object type (catalogs, schemas, tables, views, functions).
            - Each folder contains SQL scripts for creating or modifying the respective objects.
        - api-configs/:
            - Organized by API object type (jobs, alerts).
            - Each folder contains JSON or YAML files for configuring Databricks jobs and alerts.
- modules/:
    - Contains reusable modules (e.g., Python scripts, libraries, or utilities).
- notebooks/:
    - Contains notebooks organized by purpose (e.g., ETL, backup, configuration, SIT testing).


### Naming Convention
- Each folder (e.g.: tables, views, alerts) will have it's own versioned scripts.
    - SQL scripts:
        - Use S<version_number>_<object_type>__<description>.sql for SQL scripts.
        - Example: S1.0_tables__tableDDL.sql
    - API configs:
        - Use A<version_number>_<object_type>_<operation>__<description>.json for API configurations.
        - Example: A1.0_alerts_create__alertName1.json

### Deployment Workflow
- Tracking Versions:
    - Maintain a table to track executed scripts with metadata (e.g., version, checksum, type, object_type, status, inserted_datetime).
- Execution Logic:
    - Parse folders to identify scripts to execute based on version numbers.
    - Skip already executed files.
    - SQL scripts objects are deployed based on a pre-defined order in the configs.yml.

#### Open Points:
- how do we handle permissions? for api-configs objects, we can also do via API and for sql objects we can handle via sql, but how do we organize it?