from jsonschema import validate

# Input data schema for validation
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "numberOfChildren": {
            "type": "integer",
            "minimum": 0
        },
        "familyComposition": {
            "enum": ["single", "couple"]
        },
        "familyUnitInPayForDecember": {"type": "boolean"}
    },
    "required": [
        "id",
        "numberOfChildren",
        "familyComposition",
        "familyUnitInPayForDecember"
    ]
}

# Output data schema for validation
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "isEligible": {"type": "boolean"},
        "baseAmount": {"type": "number", "minimum": 0},
        "childrenAmount": {"type": "number", "minimum": 0},
        "supplementAmount": {"type": "number", "minimum": 0}
    },
    "required": [
        "id",
        "isEligible",
        "baseAmount",
        "childrenAmount",
        "supplementAmount"
    ]
}


def validate_input(input_data):
    """
    Validate input data against the predefined schema.

    Args:
        input_data (dict): Input data to validate

    Raises:
        jsonschema.ValidationError: If input does not match schema
    """
    validate(instance=input_data, schema=INPUT_SCHEMA)


def validate_output(output_data):
    """
    Validate output data against the predefined schema.

    Args:
        output_data (dict): Output data to validate

    Raises:
        jsonschema.ValidationError: If output does not match schema
    """
    validate(instance=output_data, schema=OUTPUT_SCHEMA)
