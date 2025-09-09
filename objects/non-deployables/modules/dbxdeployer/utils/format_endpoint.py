def format_endpoint(endpoint_template: str, payload: dict):
    import string
    import json

    formatter = string.Formatter()
    used_keys = [field_name for _, field_name, _, _ in formatter.parse(endpoint_template) if field_name]

    payload = json.loads(payload)

    if used_keys:
        key_values = {}

        for key in used_keys:
            payload_key = f"_{key}"
            if payload_key not in payload:
                raise ValueError(f"Missing required key '{payload_key}' for endpoint {endpoint_template}.")
        
            key_values[key] = payload.pop(payload_key)
        
        endpoint_template = endpoint_template.format(**key_values)
    
    return endpoint_template, json.dumps(payload)