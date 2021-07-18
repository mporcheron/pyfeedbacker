# -*- coding: utf-8 -*-

import unittest

from pyfeedbacker.app.model import outcomes



class TestOutcomesModel(unittest.TestCase):

    def test_outcome_fixed(self):
        """Test that a fixed outcome (i.e., a pass or fail) that is 
        programatically determined can be set and retrieved.
        """
        OUTCOME_ID_1  = 'outcome_id_1'
        KEY_1         = None
        EXPLANATION_1 = 'A sample explanation'
        VALUE_1       = 1.0
        ALL_VALUES_1  = None
        USER_INPUT_1  = False

        obj = outcomes.Outcome(outcome_id  = OUTCOME_ID_1,
                               key         = KEY_1,
                               explanation = EXPLANATION_1,
                               value       = VALUE_1,
                               all_values  = ALL_VALUES_1,
                               user_input  = USER_INPUT_1)

        self.assertEqual(obj['outcome_id'],  OUTCOME_ID_1)
        self.assertEqual(obj['key'],         KEY_1)
        self.assertEqual(obj['explanation'], EXPLANATION_1)
        self.assertEqual(obj['value'],       VALUE_1)
        self.assertEqual(obj['all_values'],  ALL_VALUES_1)
        self.assertEqual(obj['user_input'],  USER_INPUT_1)

    def test_outcome_scale(self):
        """Test that a scale outcome (i.e., a number of fixed options) that is 
        user determined can be set and retrieved.
        """
        OUTCOME_ID_2  = 'outcome_id_2'
        KEY_2         = 1
        EXPLANATION_2 = 'A sample explanation'
        VALUE_2       = 2.0
        ALL_VALUES_2  = ['A', 'B', 'C', 'D', 'E']
        USER_INPUT_2  = False

        obj = outcomes.Outcome(outcome_id  = OUTCOME_ID_2,
                               key         = KEY_2,
                               explanation = EXPLANATION_2,
                               value       = VALUE_2,
                               all_values  = ALL_VALUES_2,
                               user_input  = USER_INPUT_2)

        self.assertEqual(obj['outcome_id'],  OUTCOME_ID_2)
        self.assertEqual(obj['key'],         KEY_2)
        self.assertEqual(obj['explanation'], EXPLANATION_2)
        self.assertEqual(obj['value'],       VALUE_2)
        self.assertEqual(obj['all_values'],  ALL_VALUES_2)
        self.assertEqual(obj['user_input'],  USER_INPUT_2)

    def test_outcome_input(self):
        """Test that a inpput outcome that a user types the input can be set 
        and retrieved.
        """
        OUTCOME_ID_3  = 'outcome_id_3'
        KEY_3         = None
        EXPLANATION_3 = 'A sample explanation'
        VALUE_3       = 3.0
        ALL_VALUES_3  = None
        USER_INPUT_3  = True

        obj = outcomes.Outcome(outcome_id  = OUTCOME_ID_3,
                               key         = KEY_3,
                               explanation = EXPLANATION_3,
                               value       = VALUE_3,
                               all_values  = ALL_VALUES_3,
                               user_input  = USER_INPUT_3)

        self.assertEqual(obj['outcome_id'],  OUTCOME_ID_3)
        self.assertEqual(obj['key'],         KEY_3)
        self.assertEqual(obj['explanation'], EXPLANATION_3)
        self.assertEqual(obj['value'],       VALUE_3)
        self.assertEqual(obj['all_values'],  ALL_VALUES_3)
        self.assertEqual(obj['user_input'],  USER_INPUT_3)

    def test_outcome_setitem(self):
        """Test that updating of the data within an existing outcome works.
        """
        OUTCOME_ID_1  = 'outcome_id_1'
        KEY_1         = None
        EXPLANATION_1 = 'A sample explanation'
        VALUE_1       = 1.0
        ALL_VALUES_1  = None
        USER_INPUT_1  = False

        obj = outcomes.Outcome(outcome_id  = OUTCOME_ID_1,
                               key         = KEY_1,
                               explanation = EXPLANATION_1,
                               value       = VALUE_1,
                               all_values  = ALL_VALUES_1,
                               user_input  = USER_INPUT_1)

        self.assertEqual(obj['outcome_id'],  OUTCOME_ID_1)
        self.assertEqual(obj['key'],         KEY_1)
        self.assertEqual(obj['explanation'], EXPLANATION_1)
        self.assertEqual(obj['value'],       VALUE_1)
        self.assertEqual(obj['all_values'],  ALL_VALUES_1)
        self.assertEqual(obj['user_input'],  USER_INPUT_1)

        VALUE_1       = 2.0
        obj['value']  = VALUE_1
        self.assertEqual(obj['value'],       VALUE_1)

        EXPLANATION_1       = 'A sample updated explanation'
        obj['explanation']  = EXPLANATION_1
        self.assertEqual(obj['explanation'],  EXPLANATION_1)

    def test_outcome_float_float(self):
        """Test that updating of the value will be converted to either a float. 
        Converting object to float will store the value as float or raise a 
        ValueError.
        """
        OUTCOME_ID_1  = 'outcome_id_1'
        KEY_1         = None
        EXPLANATION_1 = 'A sample explanation'
        VALUE_1       = '1.0'
        ALL_VALUES_1  = None
        USER_INPUT_1  = False

        obj = outcomes.Outcome(outcome_id  = OUTCOME_ID_1,
                               key         = KEY_1,
                               explanation = EXPLANATION_1,
                               value       = VALUE_1,
                               all_values  = ALL_VALUES_1,
                               user_input  = USER_INPUT_1)

        VALUE_1       = 1.0
        self.assertEqual(obj['value'],       VALUE_1)

        VALUE_1       = None
        obj['value']  = VALUE_1
        with self.assertRaises(ValueError):
            float(obj)

    # def test_outcomes(self):
    #     OUTCOME_ID_1  = 'outcome_id_1'
    #     KEY_1         = 'outcome_id_1'
    #     EXPLANATION_1 = 'outcome_id_1'
    #     VALUE_1       = 'outcome_id_1'
    #     ALL_VALUES_1  = 'outcome_id_1'
    #     USER_INPUT_1  = False

    #     obj = outcomes.Outcome(outcome_id  = OUTCOME_ID_1,
    #                            key         = KEY_1,
    #                            explanation = EXPLANATION_1,
    #                            value       = VALUE_1,
    #                            all_values  = ALL_VALUES_1,
    #                            user_input  = USER_INPUT_1)
    #     self.assertEqual(obj['outcome_id'], OUTCOME_ID)
    #     self.assertEqual(obj['outcome_id'], OUTCOME_ID)
    #     self.assertEqual(obj['outcome_id'], OUTCOME_ID)


    #     STAGE_ID = 'stage_id'
    #     obj = outcomes.Outcomes(STAGE_ID)
    #     self.assertEqual(len(obj), 0)

    #     self.assertEqual(len(outcomes.Outcomes(STAGE_ID)), 0)



if __name__ == '__main__':
    unittest.main()