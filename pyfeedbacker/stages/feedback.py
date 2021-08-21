# -*- coding: utf-8 -*-

from pyfeedbacker.app import config, stage

import re



class StageFeedback(stage.HandlerEditText):
    STEP_EMPTY, STEP_COPYSUB, STEP_COPYFWK = range(0,3)

    def __init__(self, stage_id):
        """Evaluate all the feedback given and save it. This is an interactive
        stage that includes some functionality that interacts with the feedbacks model closely."""
        super().__init__(stage_id)

        self.output = stage.OutputText(u'No feedback generated.')

    def run(self):
        """Generate the feedback output."""
        self._generate_selective_feedback()

        self._feedback = self.model.feedbacks[self.submission]

        # an OutputEditText is a interactive Output with one or more edit texts,
        # that it can take from a list or dictionary.
        self.output = stage.OutputEditText(self._feedback.dict)
        self.output.callback = self.set_value
        self.output.skip_empty = True

        # This stage always passes-the user can't do anything that will lead
        # to a fail.
        result = stage.StageResult(stage.StageResult.RESULT_PASS_NONFINAL)
        result.set_output(self.output)

        return result

    def refresh(self):
        """Every time the stage is loaded, the feedback needs to be explicitly
        refreshed and pulled from the model (e.g., in case another stage has 
        changed it)."""
        self._generate_selective_feedback()
        self.output.texts = self._feedback.dict

    def _generate_selective_feedback(self):
        """Pull the feedback from the model, and parcel it up so that we have a 
        list of feedback statements, and can display each one in a separate 
        edit text."""
        config_params = config.ini.items(f'stage_{self.stage_id}')
        score = self.model.outcomes[self.submission].score

        bounds_regex = re.compile('selective_([0-9.]+)_([0-9.]+)')
        for key, value in config_params:
            if not key.startswith('selective_'):
                continue

            match = re.match(bounds_regex, key)
            if match:
                lowerbound = float(match.group(1))
                upperbound = float(match.group(2))

                fb_submission = self.model.feedbacks[self.submission]
                fb_submission[self.stage_id]['selective'] = str(upperbound)

                if score >= lowerbound and score <= upperbound:
                    fb_submission[self.stage_id]['selective'] = value
                    return

        self.set_value(self.stage_id, 'selective', '')

    def set_value(self, stage_id, feedback_id, value):
        """Callback function from the UI adapter, which saves the edited text
        back into the model.
        
        Arguments:
        stage_id -- For clarity, the stage identifier is always returned.
        feedback_id -- The unique feedback_id provided in the dictionary to 
            OutputEditText.
        value -- The new value of the feedback.
        """
        self.model.feedbacks[self.submission][stage_id][feedback_id] = value
