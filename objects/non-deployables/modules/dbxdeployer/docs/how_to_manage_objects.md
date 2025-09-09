# How to Manage Objects

Use this document as a guide on how to create the change scripts for each of the different objects.

## SQL Scripts

- **Always use SQL format** for SQL scripts.
- Place your SQL code directly in the script files.

## API Configs

The different objects managed by the API are unfortunately not set up in a straightforward way.

### Jobs

### Alerts

### Dashboards

When creating a dashboard in the UI, a file is generated. To use this file:

1. **Serialize the Dashboard JSON:**
    - **Escape Double Quotes:** Replace all `"` with `\"`.
    - **Escape Special Characters:** Replace newlines (`\n`), carriage returns (`\r`), and tabs (`\t`) with their escaped forms.

2. **Assign to Key:**
    - Use the serialized string as the value for the `serialized_dashboard` key.

**Example:**
```json
{
    "display_name": "<dashboard-name>",
    "serialized_dashboard": "{\"name\":\"My Dashboard\",\"widgets\":[{\"type\":\"chart\",\"data\":\"...\"}]}"
}
```