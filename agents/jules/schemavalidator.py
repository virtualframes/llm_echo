import json
from jsonschema import Draft7Validator, ValidationError
from functools import lru_cache

class SchemaValidationError(Exception):
    pass

@lru_cache()
def load_schema():
    with open(".github/PROVENANCE_SCHEMA.json", "r") as f:
        return json.load(f)

def validateeventor_raise(event):
    schema = load_schema()
    v = Draft7Validator(schema)
    errors = sorted(v.iter_errors(event), key=lambda e: e.path)
    if errors:
        msgs = "; ".join([f"{'/'.join(map(str,e.path))}: {e.message}" for e in errors])
        raise SchemaValidationError(msgs)
    return True
