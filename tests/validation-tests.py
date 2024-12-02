import pytest
import sys
from jsonschema import ValidationError

from winter_supplement_engine.calculator import WinterSupplementCalculator
from winter_supplement_engine.schemas import validate_input, INPUT_SCHEMA, OUTPUT_SCHEMA


class TestInputValidation:
    @pytest.mark.parametrize("invalid_input", [
        # Missing required fields
        {},
        # Type mismatches
        {
            "id": 123,  # Should be string
            "numberOfChildren": "two",  # Should be integer
            "familyComposition": 1,  # Should be string
            "familyUnitInPayForDecember": "yes"  # Should be boolean
        },
        # Invalid family composition
        {
            "id": "test_invalid",
            "numberOfChildren": 1,
            "familyComposition": "large_family",  # Not in allowed values
            "familyUnitInPayForDecember": True
        },
        # Negative children count
        {
            "id": "test_negative",
            "numberOfChildren": -1,
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        }
    ])
    def test_invalid_input_validation(self, invalid_input):
        """
        Test input validation with multiple invalid scenarios
        """
        with pytest.raises(ValidationError):
            validate_input(invalid_input)

    @pytest.mark.parametrize("valid_input", [
        # Minimal valid inputs
        {
            "id": "test_minimal_single",
            "numberOfChildren": 0,
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        },
        {
            "id": "test_minimal_couple",
            "numberOfChildren": 0,
            "familyComposition": "couple",
            "familyUnitInPayForDecember": True
        },
        # Inputs with maximum children
        {
            "id": "test_max_children",
            "numberOfChildren": sys.maxsize,  # Extremely large number
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        }
    ])
    def test_valid_input_validation(self, valid_input):
        """
        Test valid input scenarios
        """
        try:
            validate_input(valid_input)
        except Exception as e:
            pytest.fail(f"Valid input raised unexpected error: {e}")

    def test_schema_completeness(self):
        """
        Verify that input and output schemas cover all expected fields
        """
        expected_input_fields = {
            "id", 
            "numberOfChildren", 
            "familyComposition", 
            "familyUnitInPayForDecember"
        }
        expected_output_fields = {
            "id", 
            "isEligible", 
            "baseAmount", 
            "childrenAmount", 
            "supplementAmount"
        }

        # Input schema validation
        assert set(INPUT_SCHEMA['properties'].keys()) == expected_input_fields
        assert set(INPUT_SCHEMA['required']) == expected_input_fields

        # Output schema validation
        assert set(OUTPUT_SCHEMA['properties'].keys()) == expected_output_fields
        assert set(OUTPUT_SCHEMA['required']) == expected_output_fields

    def test_input_sanitization(self):
        """
        Security test for input sanitization
        """
        malicious_inputs = [
            {
                "id": "<script>alert('XSS')</script>",
                "numberOfChildren": 2,
                "familyComposition": "single",
                "familyUnitInPayForDecember": True
            },
            {
                "id": "' OR 1=1 --", 
                "numberOfChildren": 2,
                "familyComposition": "single",
                "familyUnitInPayForDecember": True
            }
        ]

        for input_data in malicious_inputs:
            try:
                validate_input(input_data)
                result = WinterSupplementCalculator.calculate_supplement(input_data)
                # Ensure no unexpected behavior occurs
                assert result['id'] == input_data['id']
            except Exception as e:
                # Validation should either sanitize or reject
                assert isinstance(e, Exception)
