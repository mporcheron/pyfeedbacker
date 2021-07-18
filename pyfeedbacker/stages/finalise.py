# -*- coding: utf-8 -*-

from pyfeedbacker.app import config, stage

import re



class StageFinalise(stage.HandlerEditText):
    STEP_EMPTY, STEP_COPYSUB, STEP_COPYFWK = range(0,3)

    def __init__(self, stage_id):
        super().__init__(stage_id)
        self.output = stage.OutputText(u'No feedback generated.')

    def run(self):
        self._generate_selective_feedback()

        self._feedback = self.model.feedbacks[self.submission]

        self.output = stage.OutputEditText(self._feedback.dict)
        self.output.callback = self.set_value
        self.output.skip_empty = True

        result = stage.StageResult(stage.StageResult.RESULT_PASS)
        result.set_output(self.output)

        return result

    def refresh(self):
        self._generate_selective_feedback()
        self.output.texts = self._feedback.dict

    def _generate_selective_feedback(self):
        config_params = config.ini.items(f'stage_{self.stage_id}')
        score = self.model.outcomes[self.submission].sum

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
        self.model['feedbacks'][self.submission][stage_id][feedback_id] = value
