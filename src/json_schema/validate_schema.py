import jsonref
import os
from json import dump
import errno
from jsonschema import Draft7Validator
from pprint import pprint


json_schema_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(json_schema_path, "job.json")

if os.name == "nt":
    base_uri = "file:///{}/".format(json_schema_path)
else:
    base_uri = "file://{}/".format(json_schema_path)

with open(file_path) as schema_file:
    my_schema = jsonref.load(schema_file, base_uri=base_uri, jsonschema=True)
    Draft7Validator.check_schema(my_schema)

    schema_dir = os.path.join(json_schema_path, "../../schema")
    if not os.path.exists(os.path.dirname(schema_dir)):
        try:
            os.makedirs(os.path.dirname(schema_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(os.path.join(schema_dir, "schema.json"), "w") as f:
        dump(my_schema, f, indent=4, sort_keys=True)
