# -*- coding: utf-8 -*-

import unittest

from pyfeedbacker.app import config
from pyfeedbacker.app.model import outcomes, feedbacks



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

        # All values should be saved as set.
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

        # All values should be saved as set.
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

        # All values should be saved as set.
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

        # All values should be saved as set.
        self.assertEqual(obj['outcome_id'],   TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(obj['key'],          TestOutcomesModel.KEY_1)
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_1)
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)
        self.assertEqual(obj['all_values'],   TestOutcomesModel.ALL_VALUES_1)
        self.assertEqual(obj['user_input'],   TestOutcomesModel.USER_INPUT_1)

        # Updating the 'value' by square brackets will update the 'value'
        TestOutcomesModel.VALUE_1           = 2.0
        obj['value']                        = TestOutcomesModel.VALUE_1
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)

        # Updating the explanation by square brackets will update the 
        # explanation
        TestOutcomesModel.EXPLANATION_1     = 'A sample updated explanation'
        obj['explanation']                  = TestOutcomesModel.EXPLANATION_1
        self.assertEqual(obj['explanation'],  TestOutcomesModel.EXPLANATION_1)

    def test_outcome_float_float(self):
        """Test that updating of the value will be converted to either a float or raise a ValueError."""
        obj = outcomes.Outcome(outcome_id   = TestOutcomesModel.OUTCOME_ID_1,
                               key          = TestOutcomesModel.KEY_1,
                               explanation  = TestOutcomesModel.EXPLANATION_1,
                               value        = TestOutcomesModel.VALUE_1,
                               all_values   = TestOutcomesModel.ALL_VALUES_1,
                               user_input   = TestOutcomesModel.USER_INPUT_1)

        config.ini.clear()

        # Updating the 'value' to a number in a string will work
        TestOutcomesModel.VALUE_1           = '1.0'
        obj['value']                        = TestOutcomesModel.VALUE_1

        TestOutcomesModel.VALUE_1           = float(TestOutcomesModel.VALUE_1)
        self.assertEqual(obj['value'],        TestOutcomesModel.VALUE_1)

        # Updating the 'value' to None will raise a ValueError
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

        # The default Outcomes object contains nothing
        self.assertEqual(len(ocs_1), 0)

        # If we insert an outcome with an ID but set a differnet key, the 
        # outcome's ID should be updated in the outcome object, and the original
        # outcome set inside Outcomes should be replaced
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_4] = oc_1

        self.assertEqual(len(ocs_1), 1)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_4)

        # The sum of the single outcome should be the value
        self.assertEqual(ocs_1.sum, oc_1['value'])

        # It should be possible to insert two different outcomes with different
        # outcome identifiers
        oc_1['outcome_id']  = TestOutcomesModel.OUTCOME_ID_1

        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_4] = oc_4

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(oc_4['outcome_id'], TestOutcomesModel.OUTCOME_ID_4)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_4], oc_4)

        # The sum of the multiple outcomes will be correct
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

        # Two different outcomes can be added with different identifiers
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_2] = oc_2

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(oc_2['outcome_id'], TestOutcomesModel.OUTCOME_ID_2)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_2], oc_2)

        # The sum of the two outcomes will be correct
        expected_sum = oc_1['value'] + oc_2['value']
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # When a maximum score is applied, the score will not exceed this
        config_section = f'stage_{TestOutcomesModel.STAGE_ID_1}'
        expected_sum = 1.0
        config.ini.add_section(config_section)
        config.ini.set(config_section, 'score_max', str(expected_sum))
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # When a minimum score is applied, the score will be at least this (not 
        # that this may breach the maximum score if minimum > maximum)
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

        # Two items can be added to the model
        ocs_1[TestOutcomesModel.OUTCOME_ID_1] = oc_1
        ocs_1[TestOutcomesModel.OUTCOME_ID_3] = oc_3

        self.assertEqual(len(ocs_1), 2)
        self.assertEqual(oc_1['outcome_id'], TestOutcomesModel.OUTCOME_ID_1)
        self.assertEqual(oc_3['outcome_id'], TestOutcomesModel.OUTCOME_ID_3)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_1], oc_1)
        self.assertEqual(ocs_1[TestOutcomesModel.OUTCOME_ID_3], oc_3)

        # The sum of the two outcomes is correct
        expected_sum = oc_1['value'] + oc_3['value']
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # When a maximum score is applied, the score will not exceed this
        config_section = f'stage_{TestOutcomesModel.STAGE_ID_1}'
        expected_sum = 1.0
        config.ini.add_section(config_section)
        config.ini.set(config_section, 'score_max', str(expected_sum))
        self.assertEqual(ocs_1.sum, expected_sum)
        self.assertEqual(float(ocs_1), expected_sum)

        # When a minimum score is applied, the score will be at least this (not 
        # that this may breach the maximum score if minimum > maximum)
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

        # An OutcomesByStage container can be created and has no values by 
        # default
        obs = outcomes.OutcomesByStage(
            parent_data_id                  = TestOutcomesModel.SUBMISSION_1)

        self.assertEqual(len(obs), 0)

        # Two Outcomes objects can be added
        obs[TestOutcomesModel.STAGE_ID_1] = ocs_1
        obs[TestOutcomesModel.STAGE_ID_2] = ocs_2

        self.assertEqual(len(obs), 2)
        self.assertEqual(obs[TestOutcomesModel.STAGE_ID_1], ocs_1)
        self.assertEqual(obs[TestOutcomesModel.STAGE_ID_2], ocs_2)

        # The sum of the two outcomes is correctly passed through to the 
        # OutcomesByStage container
        expected_sum = ocs_1.sum + ocs_2.sum
        self.assertEqual(obs.sum, expected_sum)
        self.assertEqual(float(obs), expected_sum)

        # When a maximum score is applied, the score will not exceed this
        config_section = 'assessment'
        expected_sum = 1.0
        config.ini.add_section(config_section)
        config.ini.set(config_section, 'score_max', str(expected_sum))
        self.assertEqual(obs.sum, expected_sum)
        self.assertEqual(float(obs), expected_sum)

        # When a minimum score is applied, the score will be at least this (not 
        # that this may breach the maximum score if minimum > maximum)
        expected_sum = 10.0
        config.ini.set(config_section, 'score_min', str(expected_sum))
        self.assertEqual(obs.sum, expected_sum)
        self.assertEqual(float(obs), expected_sum)



class TestFeedbacksModel(unittest.TestCase):
    FEEDBACK_ID_1  = 'feedback_id_1'
    FEEDBACK_VAL_1 = 'A sample feedback.'

    FEEDBACK_ID_2  = 'outcome_id_2'
    FEEDBACK_VAL_2 = 'A second feedback with a newline after it.\n'

    FEEDBACK_ID_3  = 'outcome_id_3'
    FEEDBACK_VAL_3 = 'A third feedback with a escaped newline after it.\\n'

    FEEDBACK_ID_4  = 'outcome_id_4'
    FEEDBACK_VAL_4 = 'A forth feedback with a blank line in the\n\nmiddle.'

    STAGE_ID_1  = 'stage_id_1'
    STAGE_ID_2  = 'stage_id_2'

    SUBMISSION_1  = 'submission_1234'
    SUBMISSION_2  = 'submission_5678'

    def test_feedbacks(self):
        """Test that a Feedbacks object can be created and can contain multiple feedback sentences."""
        fb_1 = feedbacks.Feedbacks(
                            parent_data_id  = TestFeedbacksModel.STAGE_ID_1)

        config.ini.clear()

        # No values by default
        self.assertEqual(len(fb_1), 0)

        # Add one set of feedback with a trailing space added after it
        fb_1[TestFeedbacksModel.FEEDBACK_ID_1] = \
             TestFeedbacksModel.FEEDBACK_VAL_1

        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '

        self.assertEqual(len(fb_1), 1)
        self.assertEqual(str(fb_1), expected_value)

        # Add a second feedback which includes a new line at the end of it, 
        # which will produce a string that is both feedbacks separated by a 
        # space and a trailing new line (new lines should not start with a 
        # space)
        fb_1[TestFeedbacksModel.FEEDBACK_ID_2] = \
             TestFeedbacksModel.FEEDBACK_VAL_2

        self.assertEqual(len(fb_1), 2)

        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_2
        self.assertEqual(str(fb_1), expected_value)

        # Add a feedback with an escaped new line (\\n), which is done by the
        # python configparser library. The escaped new line should be replaced
        # with an actual newline (\n)
        fb_1[TestFeedbacksModel.FEEDBACK_ID_3] = \
             TestFeedbacksModel.FEEDBACK_VAL_3

        self.assertEqual(len(fb_1), 3)

        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_2
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_3.replace('\\n', '\n')
        self.assertEqual(str(fb_1), expected_value)

        # Add a feedback with a blank line (\n\n) in the middle but not one at
        # the end (thus there should be a trailing space)
        fb_1[TestFeedbacksModel.FEEDBACK_ID_4] = \
             TestFeedbacksModel.FEEDBACK_VAL_4

        self.assertEqual(len(fb_1), 4)

        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_2
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_3.replace('\\n', '\n')
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_4 + ' '
        self.assertEqual(str(fb_1), expected_value)

    def test_feedbacks_by_stage(self):
        """Test that a Feedbacks object can be created and can contain multiple feedback sentences."""
        # Create two feedback objects
        fb_1 = feedbacks.Feedbacks(
                            parent_data_id  = TestFeedbacksModel.STAGE_ID_1)

        fb_1[TestFeedbacksModel.FEEDBACK_ID_1] = \
             TestFeedbacksModel.FEEDBACK_VAL_1
        fb_1[TestFeedbacksModel.FEEDBACK_ID_2] = \
             TestFeedbacksModel.FEEDBACK_VAL_2

        fb_2 = feedbacks.Feedbacks(
                            parent_data_id  = TestFeedbacksModel.STAGE_ID_2)

        fb_2[TestFeedbacksModel.FEEDBACK_ID_3] = \
             TestFeedbacksModel.FEEDBACK_VAL_3
        fb_2[TestFeedbacksModel.FEEDBACK_ID_4] = \
             TestFeedbacksModel.FEEDBACK_VAL_4

        self.assertEqual(len(fb_1), 2)
        self.assertEqual(len(fb_2), 2)
        
        # Create a FeedbacksByStage container
        fbs = feedbacks.FeedbackByStage(
                            parent_data_id  = TestFeedbacksModel.SUBMISSION_1)

        self.assertEquals(len(fbs), 0)

        # Add one of the Feedbacks objects
        fbs[TestFeedbacksModel.STAGE_ID_1] = fb_1

        self.assertEquals(len(fbs), 1)
        self.assertEquals(fbs[TestFeedbacksModel.STAGE_ID_1], fb_1)

        # The string conversion of the object should be the two objects
        # combined, with a space between them and then two new line characters
        # added to the end
        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_2 + '\n\n'
        self.assertEquals(str(fbs), expected_value)

        # If the same object is applied to a different stage identifier,
        # is the object stage identifier updated
        fbs[TestFeedbacksModel.STAGE_ID_2] = fb_1

        self.assertEquals(len(fbs), 1)
        self.assertEquals(fbs[TestFeedbacksModel.STAGE_ID_2], fb_1)
        self.assertEquals(TestFeedbacksModel.STAGE_ID_2, fb_1.stage_id)

        # The string conversion of the object should be the two Feedback objects
        # combined, with a space between them and then two new line characters
        # added to the end
        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_2 + '\n\n'
        self.assertEquals(str(fbs), expected_value)

        # Revert back to the correct stage ID
        fb_1._parent_data_id = TestFeedbacksModel.STAGE_ID_1

        # Add two Feedbacks objects
        fbs[TestFeedbacksModel.STAGE_ID_1] = fb_1
        fbs[TestFeedbacksModel.STAGE_ID_2] = fb_2

        self.assertEquals(len(fbs), 2)
        self.assertEquals(fbs[TestFeedbacksModel.STAGE_ID_1], fb_1)
        self.assertEquals(fbs[TestFeedbacksModel.STAGE_ID_2], fb_2)

        # The string conversion of the object should be the four Feedback 
        # objects combined, with a space between them and then two new line 
        # characters added to the end
        expected_value  = TestFeedbacksModel.FEEDBACK_VAL_1 + ' '
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_2 + '\n\n'
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_3.replace('\\n', '\n')
        expected_value += TestFeedbacksModel.FEEDBACK_VAL_4 + ' \n\n'
        self.assertEquals(str(fbs), expected_value)


if __name__ == '__main__':
    unittest.main()