### Folder Descriptions

- deployables/:
    - Contains all deployable assets.
        - sql-scripts/:
            - Organized by Unity Catalog object type (catalogs, schemas, tables, views, functions).
            - If new objects need to be versioned, just add a new folder for the object.
            - Each folder contains SQL scripts for creating or modifying the respective objects.
                - Or any changes related to the object, eg.: backup of a table.
            - Each folder is versioned separately.
        - api-configs/:
            - Organized by API object type (jobs, alerts).
            - If new objects need to be versioned, just add a new folder for the object.
            - Each folder contains the JSON definition for each object.
        - permissions/:
            - Permissions to all objects in a workspace are stored in a DB table.
            - Add/update/delete permissions to an object by creating an update script.
            - Permissions job checks every day for permissions where the status = PENDING.

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
    - Permissions:
        - Use P<version_number>__<description>.sql for SQL scripts.
        - Example: P1.0_permissionsToTableABC.sql

### Deployment Workflow
- Tracking Versions:
    - Maintain a table to track executed scripts with metadata (e.g., version, checksum, type, object_type, status, inserted_datetime).
- Execution Logic:
    - Parse folders to identify scripts to execute based on version numbers.
    - Skip already executed files.
    - Objects are deployed based on a pre-defined order in the configs.yml.
    - API endpoints are defined in api-configs.yml making the tool easily extendable for other API-deployable objects.
---
### Current Limitations:
- Each SQL script can only contain 1 SQL statement.