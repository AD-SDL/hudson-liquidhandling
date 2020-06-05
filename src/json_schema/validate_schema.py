import jsonref
import os
from jsonschema import Draft7Validator
from pprint import pprint


json_schema_path = os.path.abspath(os.path.dirname(__file__))
step_path = os.path.join(json_schema_path, "SoloSoft/steps/step.json")
if os.name == 'nt':
    base_uri = 'file:///{}/'.format(json_schema_path)
else:
    base_uri = 'file://{}/'.format(json_schema_path)

print(base_uri)
with open(step_path) as schema_file:
    my_schema = jsonref.loads(
        schema_file.read(), base_uri=base_uri, jsonschema=True
    )
    # pprint(my_schema)
    Draft7Validator.check_schema(my_schema)
