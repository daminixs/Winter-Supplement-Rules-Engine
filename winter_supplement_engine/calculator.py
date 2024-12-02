from typing import Dict, Union


class WinterSupplementCalculator:
    """
    Calculator for Winter Supplement eligibility and amount determination.
    """
    
    SUPPLEMENT_RATES = {
        "single": 60.0,
        "couple": 120.0,
        "child_rate": 20.0
    }
    
    @classmethod
    def calculate_supplement(cls, input_data: Dict[str, Union[str, int, bool]]) -> Dict[str, Union[str, bool, float]]:
        """
        Calculate winter supplement based on family composition and children.
        
        Args:
            input_data (dict): Client eligibility input data
        
        Returns:
            dict: Supplement calculation results
        """
        # Check basic eligibility
        if not input_data['familyUnitInPayForDecember']:
            return {
                "id": input_data['id'],
                "isEligible": False,
                "baseAmount": 0.0,
                "childrenAmount": 0.0,
                "supplementAmount": 0.0
            }
        
        # Base amount calculation
        base_amount = cls.SUPPLEMENT_RATES.get(input_data['familyComposition'], 0.0)
        
        # Children amount calculation
        children_amount = input_data['numberOfChildren'] * cls.SUPPLEMENT_RATES['child_rate']
        
        return {
            "id": input_data['id'],
            "isEligible": True,
            "baseAmount": base_amount,
            "childrenAmount": children_amount,
            "supplementAmount": base_amount + children_amount
        }
