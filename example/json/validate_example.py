import jsonref
import os
from json import dump
import errno
from jsonschema import Draft7Validator, validate
from pprint import pprint


current_directory = os.path.abspath(os.path.dirname(__file__))
schema_file_path = os.path.join(current_directory, "../../schema/schema.json")

with open(schema_file_path) as schema_file:
    my_schema = jsonref.load(schema_file, jsonschema=True)

    file_path = os.path.join(current_directory, "solo_soft_example.json")
    with open(file_path) as json_file:
        validate(instance=jsonref.load(json_file), schema=my_schema)
