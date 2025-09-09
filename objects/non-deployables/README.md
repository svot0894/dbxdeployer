# Non-Deployable Objects

This folder contains objects that do not require a deployment process -> [Asset types supported by Git folders](https://learn.microsoft.com/en-us/azure/databricks/repos/supported-artifact-types#asset-types-supported-by-git-folders).

- Databricks will automatically recognize these objects.
- Changes are tracked and managed by the platform.
- Manual deployment steps are not necessary.

## Current supported objects:
- Files
- Notebooks
- Folders
- Query (Public Preview)
- Dashboards (Public Preview)
- Alerts (Beta)

## Note
Objects in this directory are handled by Databricks' native version control (Git folders).