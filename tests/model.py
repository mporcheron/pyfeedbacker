# -*- coding: utf-8 -*-

import unittest

from pyfeedbacker.app import config
from pyfeedbacker.app.model import outcomes



class TestOutcomesModel(unittest.TestCase):
    OUTCOME_ID_1  = 'outcome_id_1'
    KEY_1         = None
    EXPLANATION_1 = 'A sample explanation'
    VALUE_1       = 1.0
    ALL_VALUES_1  = None
    USER_INPUT_1  = False

    OUTCOME_ID_2  = 'outcome_id_2'
    KEY_2         = 1
    EXPLANATION_2 = 'A sample explanation'
    VALUE_2       = 2.0
    ALL_VALUES_2  = [('A', 0.0), ('B', 2.0), ('C', 4.0), ('D', 6.0), ('E', 8.0)]
    USER_INPUT_2  = False

    OUTCOME_ID_3  = 'outcome_id_3'
    KEY_3         = None
    EXPLANATION_3 = 'A sample explanation'
    VALUE_3       = 3.0
    ALL_VALUES_3  = None
    USER_INPUT_3  = True

    OUTCOME_ID_4  = 'outcome_id_4'
    KEY_4         = None
    EXPLANATION_4 = 'A sample explanation'
    VALUE_4       = 1.5
    ALL_VALUES_4  = None
    USER_INPUT_4  = False

    STAGE_ID_1  = 'stage_id_1'
    STAGE_ID_2  = 'stage_id_2'

    SUBMISSION_1  = 'submission_1234'
    SUBMISSION_2  = 'submission_5678'

    def test_outcome_fixed(self):
        """Test that a fixed outcome (i.e., a pass or fail) that is programatically determined can be set and retrieved."""
        obj = outcomes.Outcome(outcome_id   = TestOutcomesModel.OUTCOME_ID_1,
                               key          = TestOutcomesModel.KEY_1,
                               explanation  = TestOutcomesModel.EXPLANATION_1,
                               value        = TestOutcomesModel.VALUE_1,
                               all_values   = TestOutcomesModel.ALL_VALUES_1,
                               user_input   = TestOutcomesModel.USER_INPUT_1)

        config.ini.clear()

        self.assertEqual(obj['outcome_id'],   TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(obj['key'],          TestOutcomesModel.KEY_1)
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_1)
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)
        self.assertEqual(obj['all_values'],   TestOutcomesModel.ALL_VALUES_1)
        self.assertEqual(obj['user_input'],   TestOutcomesModel.USER_INPUT_1)

    def test_outcome_scale(self):
        """Test that a scale outcome (i.e., a number of fixed options) that is  user determined can be set and retrieved."""
        obj = outcomes.Outcome(outcome_id   = TestOutcomesModel.OUTCOME_ID_2,
                               key          = TestOutcomesModel.KEY_2,
                               explanation  = TestOutcomesModel.EXPLANATION_2,
                               value        = TestOutcomesModel.VALUE_2,
                               all_values   = TestOutcomesModel.ALL_VALUES_2,
                               user_input   = TestOutcomesModel.USER_INPUT_2)

        config.ini.clear()

        self.assertEqual(obj['outcome_id'],   TestOutcomesModel.OUTCOME_ID_2)
        self.assertEqual(obj['key'],          TestOutcomesModel.KEY_2)
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_2)
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_2)
        self.assertEqual(obj['all_values'],   TestOutcomesModel.ALL_VALUES_2)
        self.assertEqual(obj['user_input'],   TestOutcomesModel.USER_INPUT_2)

    def test_outcome_input(self):
        """Test that a inpput outcome that a user types the input can be set  and retrieved."""
        obj = outcomes.Outcome(outcome_id   = TestOutcomesModel.OUTCOME_ID_3,
                               key          = TestOutcomesModel.KEY_3,
                               explanation  = TestOutcomesModel.EXPLANATION_3,
                               value        = TestOutcomesModel.VALUE_3,
                               all_values   = TestOutcomesModel.ALL_VALUES_3,
                               user_input   = TestOutcomesModel.USER_INPUT_3)

        config.ini.clear()

        self.assertEqual(obj['outcome_id'],   TestOutcomesModel.OUTCOME_ID_3)
        self.assertEqual(obj['key'],          TestOutcomesModel.KEY_3)
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_3)
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_3)
        self.assertEqual(obj['all_values'],   TestOutcomesModel.ALL_VALUES_3)
        self.assertEqual(obj['user_input'],   TestOutcomesModel.USER_INPUT_3)

    def test_outcome_setitem(self):
        """Test that updating of the data within an existing outcome works."""
        obj = outcomes.Outcome(outcome_id   = TestOutcomesModel.OUTCOME_ID_1,
                               key          = TestOutcomesModel.KEY_1,
                               explanation  = TestOutcomesModel.EXPLANATION_1,
                               value        = TestOutcomesModel.VALUE_1,
                               all_values   = TestOutcomesModel.ALL_VALUES_1,
                               user_input   = TestOutcomesModel.USER_INPUT_1)

        config.ini.clear()

        self.assertEqual(obj['outcome_id'],   TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(obj['key'],          TestOutcomesModel.KEY_1)
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_1)
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)
        self.assertEqual(obj['all_values'],   TestOutcomesModel.ALL_VALUES_1)
        self.assertEqual(obj['user_input'],   TestOutcomesModel.USER_INPUT_1)

        TestOutcomesModel.VALUE_1           = 2.0
        obj['value']                        = TestOutcomesModel.VALUE_1
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)

        TestOutcomesModel.EXPLANATION_1     = 'A sample updated explanation'
        obj['explanation']                  = TestOutcomesModel.EXPLANATION_1
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_1)

    def test_outcome_float_float(self):
        """Test that updating of the value will be converted to either a float.  Converting object to float will store the value as float or raise a ValueError.
        """
        obj = outcomes.Outcome(outcome_id   = TestOutcomesModel.OUTCOME_ID_1,
                               key          = TestOutcomesModel.KEY_1,
                               explanation  = TestOutcomesModel.EXPLANATION_1,
                               value        = TestOutcomesModel.VALUE_1,
                               all_values   = TestOutcomesModel.ALL_VALUES_1,
                               user_input   = TestOutcomesModel.USER_INPUT_1)

        config.ini.clear()

        TestOutcomesModel.VALUE_1           = 1.0
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)

        TestOutcomesModel.VALUE_1           = None
        obj['value']                        = TestOutcomesModel.VALUE_1
        with self.assertRaises(ValueError):
            float(obj)

    def test_outcomes_fixed(self):
        """Test that creation of an Outcomes object that will store the outcomes for a particular stage. There are two fixed outcome objects stored. The sum property will be tested too."""
        oc_1 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_1,
                                key         = TestOutcomesModel.KEY_1,
                                explanation = TestOutcomesModel.EXPLANATION_1,
                                value       = TestOutcomesModel.VALUE_1,
                                all_values  = TestOutcomesModel.ALL_VALUES_1,
                                user_input  = TestOutcomesModel.USER_INPUT_1)

        oc_4 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_4,
                               key          = TestOutcomesModel.KEY_4,
                               explanation  = TestOutcomesModel.EXPLANATION_4,
                               value        = TestOutcomesModel.VALUE_4,
                               all_values   = TestOutcomesModel.ALL_VALUES_4,
                               user_input   = TestOutcomesModel.USER_INPUT_4)

        ocs_1 = outcomes.Outcomes(
                            parent_data_id  = TestOutcomesModel.STAGE_ID_1)

        config.ini.clear()

        self.assertEqual(len(ocs_1), 0)

        # if we insert an outcome with an ID but set a differnet key, the 
        # outcome's ID should be updated in the outcome object, and the original
        # outcome set inside Outcomes should be replaced
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_4] = oc_1

        self.assertEqual(len(ocs_1), 1)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_4)

        # test the sum
        self.assertEqual(ocs_1.sum, oc_1['value'])

        # test inserting two different items
        oc_1['outcome_id']  = TestOutcomesModel.OUTCOME_ID_1

        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_4] = oc_4

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(oc_4['outcome_id'], TestOutcomesModel.OUTCOME_ID_4)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_4], oc_4)

        # test the sum
        expected_sum = oc_1['value'] + oc_4['value']
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

    def test_outcomes_scales(self):
        """Test that creation of an Outcomes object that will store the outcomes for a particular stage. There is one fixed outcome objects and one scaled outcome object stored. The sum property will be tested too, ensuring it works and also applies any configured min/max values."""
        oc_1 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_1,
                                key         = TestOutcomesModel.KEY_1,
                                explanation = TestOutcomesModel.EXPLANATION_1,
                                value       = TestOutcomesModel.VALUE_1,
                                all_values  = TestOutcomesModel.ALL_VALUES_1,
                                user_input  = TestOutcomesModel.USER_INPUT_1)

        oc_2 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_2,
                                key         = TestOutcomesModel.KEY_2,
                                explanation = TestOutcomesModel.EXPLANATION_2,
                                value       = TestOutcomesModel.VALUE_2,
                                all_values  = TestOutcomesModel.ALL_VALUES_2,
                                user_input  = TestOutcomesModel.USER_INPUT_2)

        ocs_1 = outcomes.Outcomes(
                            parent_data_id  = TestOutcomesModel.STAGE_ID_1)

        config.ini.clear()

        # add the two items
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_2] = oc_2

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(oc_2['outcome_id'], TestOutcomesModel.OUTCOME_ID_2)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_2], oc_2)

        # test the sum
        expected_sum = oc_1['value'] + oc_2['value']
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # test with a maximum score
        config_section = f'stage_{TestOutcomesModel.STAGE_ID_1}'
        expected_sum = 1.0
        config.ini.add_section(config_section)
        config.ini.set(config_section, 'score_max', str(expected_sum))
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # test with a mininum score
        config_section = f'stage_{TestOutcomesModel.STAGE_ID_1}'
        expected_sum = 10.0
        config.ini.set(config_section, 'score_min', str(expected_sum))
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

    def test_outcomes_input(self):
        """Test that creation of an Outcomes object that will store the outcomes for a particular stage. There is one fixed outcome objects and one input outcome object stored. The sum property will be tested too, ensuring it works and also applies any configured min/max values."""
        oc_1 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_1,
                                key         = TestOutcomesModel.KEY_1,
                                explanation = TestOutcomesModel.EXPLANATION_1,
                                value       = TestOutcomesModel.VALUE_1,
                                all_values  = TestOutcomesModel.ALL_VALUES_1,
                                user_input  = TestOutcomesModel.USER_INPUT_1)

        oc_3 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_3,
                                key         = TestOutcomesModel.KEY_3,
                                explanation = TestOutcomesModel.EXPLANATION_3,
                                value       = TestOutcomesModel.VALUE_3,
                                all_values  = TestOutcomesModel.ALL_VALUES_3,
                                user_input  = TestOutcomesModel.USER_INPUT_3)

        ocs_1 = outcomes.Outcomes(
                            parent_data_id  = TestOutcomesModel.STAGE_ID_1)

        config.ini.clear()

        # add the two items
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_3] = oc_3

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(oc_3['outcome_id'], TestOutcomesModel.OUTCOME_ID_3)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_3], oc_3)

        # test the sum
        expected_sum = oc_1['value'] + oc_3['value']
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # test with a maximum score
        config_section = f'stage_{TestOutcomesModel.STAGE_ID_1}'
        expected_sum = 1.0
        config.ini.add_section(config_section)
        config.ini.set(config_section, 'score_max', str(expected_sum))
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # test with a mininum score
        config_section = f'stage_{TestOutcomesModel.STAGE_ID_1}'
        expected_sum = 10.0
        config.ini.set(config_section, 'score_min', str(expected_sum))
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

    def test_outcomes_by_stage(self):
        """Test that creation of an OutcomesByStage object that will store the outcomes for multiple stages. A number of outcomes will be added. The sum property will be tested, ensuring it works and also applies any configured min/max values."""
        oc_1 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_1,
                                key         = TestOutcomesModel.KEY_1,
                                explanation = TestOutcomesModel.EXPLANATION_1,
                                value       = TestOutcomesModel.VALUE_1,
                                all_values  = TestOutcomesModel.ALL_VALUES_1,
                                user_input  = TestOutcomesModel.USER_INPUT_1)

        oc_2 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_2,
                                key         = TestOutcomesModel.KEY_2,
                                explanation = TestOutcomesModel.EXPLANATION_2,
                                value       = TestOutcomesModel.VALUE_2,
                                all_values  = TestOutcomesModel.ALL_VALUES_2,
                                user_input  = TestOutcomesModel.USER_INPUT_2)

        oc_3 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_3,
                                key         = TestOutcomesModel.KEY_3,
                                explanation = TestOutcomesModel.EXPLANATION_3,
                                value       = TestOutcomesModel.VALUE_3,
                                all_values  = TestOutcomesModel.ALL_VALUES_3,
                                user_input  = TestOutcomesModel.USER_INPUT_3)

        oc_4 = outcomes.Outcome(outcome_id  = TestOutcomesModel.OUTCOME_ID_4,
                               key          = TestOutcomesModel.KEY_4,
                               explanation  = TestOutcomesModel.EXPLANATION_4,
                               value        = TestOutcomesModel.VALUE_4,
                               all_values   = TestOutcomesModel.ALL_VALUES_4,
                               user_input   = TestOutcomesModel.USER_INPUT_4)

        ocs_1 = outcomes.Outcomes(
                            parent_data_id  = TestOutcomesModel.STAGE_ID_1)

        ocs_2 = outcomes.Outcomes(
                            parent_data_id  = TestOutcomesModel.STAGE_ID_2)

        config.ini.clear()

        # add two Outcomes to each stage
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_2] = oc_2

        ocs_2[TestOutcomesModel.OUTCOME_ID_3] = oc_3
        ocs_2[TestOutcomesModel.OUTCOME_ID_4] = oc_4

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(len(ocs_2), 2)

        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_2], oc_2)

        self.assertEqual(ocs_2[TestOutcomesModel.OUTCOME_ID_3], oc_3)
        self.assertEqual(ocs_2[TestOutcomesModel.OUTCOME_ID_4], oc_4)

        # create the OutcomesByStage container
        obs = outcomes.OutcomesByStage(
            parent_data_id                  = TestOutcomesModel.SUBMISSION_1)

        obs[TestOutcomesModel.STAGE_ID_1] = ocs_1
        obs[TestOutcomesModel.STAGE_ID_2] = ocs_2

        # test the values are inserted
        self.assertEqual(len(obs), 2)

        self.assertEqual(obs[TestOutcomesModel.STAGE_ID_1], ocs_1)
        self.assertEqual(obs[TestOutcomesModel.STAGE_ID_2], ocs_2)

        # test the sum
        expected_sum = ocs_1.sum + ocs_2.sum
        self.assertEqual(obs.sum, expected_sum)
        self.assertEqual(float(obs), expected_sum)

        # test with a maximum score
        config_section = 'assessment'
        expected_sum = 1.0
        config.ini.add_section(config_section)
        config.ini.set(config_section, 'score_max', str(expected_sum))
        self.assertEqual(obs.sum, expected_sum)
        self.assertEqual(float(obs), expected_sum)

        # test with a mininum score
        expected_sum = 10.0
        config.ini.set(config_section, 'score_min', str(expected_sum))
        self.assertEqual(obs.sum, expected_sum)
        self.assertEqual(float(obs), expected_sum)


        

if __name__ == '__main__':
    unittest.main()