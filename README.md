# dbxdeployer

dbxdeployer is a Python CLI for planning, validating, and safely applying ordered SQL deployments to Unity Catalog, with immutable history, checksum enforcement, concurrency protection, durable execution records, and controlled recovery.

### Deployable objects

- Catalogs
- Schemas
- Tables
- Views
- Materialized views
- Functions
- Volumes
- Permissions


### Naming Convention
Use the following naming convention to your created files:
- ```V00000X__<description-of-changes-applied>.sql```

### Variables in Scripts
dbxdeployer supports the jinja engine for variable replacement. To use a variable in a change script, use this syntax anywhere in the script: `{{ variable1 }}`. You can pass variables by defining them in the config.yml file.

### Deployment Rules
- A deployment script is immutable.
- A successfully applied migration is never executed automatically again.
- A previously applied deployment whose checksum has changed blocks deployment.
- Migrations are applied in one deterministic global order.
- A later migration cannot execute if an earlier pending migration failed.
- At most, one deployment run may actively apply migrations for a target environment.
- Every attempted migration has a durable execution record.
- Dry-run performs no writes to either objects or migration metadata.
- Unknown execution outcomes are never silently retried.
- Recovery requires an explicit user decision.
- A migration cannot be removed from history without detection.
- The same migration source revision should produce the same deployment plan.
---
### Current Limitations:
- Each SQL script can only contain 1 SQL statement (Databricks REST API limitation).