import pytest
from winter_supplement_engine.calculator import WinterSupplementCalculator


class TestSupplementCalculations:
    @pytest.mark.parametrize("input_data, expected", [
        # Single person scenarios
        ({
            "id": "single_user_1",
            "numberOfChildren": 0,
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        }, {
            "id": "single_user_1",
            "isEligible": True,
            "baseAmount": 60.0,
            "childrenAmount": 0.0,
            "supplementAmount": 60.0
        }),
        # Couple with children scenarios
        ({
            "id": "couple_with_kids",
            "numberOfChildren": 2,
            "familyComposition": "couple",
            "familyUnitInPayForDecember": True
        }, {
            "id": "couple_with_kids",
            "isEligible": True,
            "baseAmount": 120.0,
            "childrenAmount": 40.0,
            "supplementAmount": 160.0
        }),
        # Ineligible scenarios
        ({
            "id": "ineligible_user",
            "numberOfChildren": 1,
            "familyComposition": "single",
            "familyUnitInPayForDecember": False
        }, {
            "id": "ineligible_user",
            "isEligible": False,
            "baseAmount": 0.0,
            "childrenAmount": 0.0,
            "supplementAmount": 0.0
        })
    ])
    def test_calculate_supplement(self, input_data, expected):
        """
        Test supplement calculation with various scenarios
        """
        result = WinterSupplementCalculator.calculate_supplement(input_data)
        assert result == expected

    def test_calculation_edge_cases(self):
        """
        Comprehensive edge case calculation testing
        """
        test_cases = [
            # Zero children scenarios
            {
                "id": "zero_children_single",
                "numberOfChildren": 0,
                "familyComposition": "single",
                "familyUnitInPayForDecember": True,
                "expected_base": 60.0,
                "expected_children": 0.0
            },
            {
                "id": "zero_children_couple",
                "numberOfChildren": 0,
                "familyComposition": "couple",
                "familyUnitInPayForDecember": True,
                "expected_base": 120.0,
                "expected_children": 0.0
            },
            # Large number of children scenario
            {
                "id": "max_children_single",
                "numberOfChildren": 500,
                "familyComposition": "single",
                "familyUnitInPayForDecember": True,
                "expected_base": 60.0,
                "expected_children": 10000.0
            },
            # Not in pay for December
            {
                "id": "not_in_pay",
                "numberOfChildren": 3,
                "familyComposition": "couple",
                "familyUnitInPayForDecember": False,
                "expected_base": 0.0,
                "expected_children": 0.0
            }
        ]

        for case in test_cases:
            result = WinterSupplementCalculator.calculate_supplement(case)
            
            if not case['familyUnitInPayForDecember']:
                # Ineligible scenario checks
                assert result['isEligible'] == False, f"Failed for {case['id']}"
                assert result['supplementAmount'] == 0.0, f"Failed for {case['id']}"
            else:
                # Validate calculation logic for eligible scenarios
                assert result['isEligible'] == True, f"Failed for {case['id']}"
                assert result['baseAmount'] == case['expected_base'], f"Failed base amount for {case['id']}"
                assert result['childrenAmount'] == case['expected_children'], f"Failed children amount for {case['id']}"
                assert result['supplementAmount'] == case['expected_base'] + case['expected_children'], f"Failed total supplement for {case['id']}"

    def test_calculation_type_safety(self):
        """
        Ensure calculation returns correct data types
        """
        input_data = {
            "id": "type_safety_test",
            "numberOfChildren": 2,
            "familyComposition": "couple",
            "familyUnitInPayForDecember": True
        }

        result = WinterSupplementCalculator.calculate_supplement(input_data)

        # Type checks
        assert isinstance(result['id'], str), "ID should be a string"
        assert isinstance(result['isEligible'], bool), "isEligible should be a boolean"
        assert all(isinstance(val, float) for val in [
            result['baseAmount'], 
            result['childrenAmount'], 
            result['supplementAmount']
        ]), "Amount fields should be floats"

    def test_immutability(self):
        """
        Verify that calculation does not mutate the original input data
        """
        input_data = {
            "id": "immutability_test",
            "numberOfChildren": 2,
            "familyComposition": "couple",
            "familyUnitInPayForDecember": True
        }
        
        original_input = input_data.copy()
        WinterSupplementCalculator.calculate_supplement(input_data)
        
        # Ensure input data remains unchanged
        assert input_data == original_input, "Input data should not be modified"
