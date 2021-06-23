# -*- coding: utf-8 -*-

from app import config, stage

import re


class StageFinalise(stage.HandlerEditText):
    TAG = u'finalise'
    STEP_EMPTY, STEP_COPYSUB, STEP_COPYFWK = range(0,3)
    
    def __init__(self):
        self.output = stage.OutputText(u'No feedback generated.')

    def run(self):
        self._generate_selective_feedback()
        
        self.output = stage.OutputEditText(self.model.raw_feedback)
        self.output.set_callback(self.set_value)
        result = stage.StageResult(stage.StageResult.RESULT_PASS)
        result.set_output(self.output)
        return result

    def refresh(self):
        self._generate_selective_feedback()
        self.output.texts = self.model.raw_feedback

    def _generate_selective_feedback(self):
        config_params = config.ini.items(f'stage_{StageFinalise.TAG}')
        score = self.model.score

        bounds_regex = re.compile('selective_([0-9.]+)_([0-9.]+)')
        for key, value in config_params:
            if not key.startswith('selective_'):
                continue
            
            match = re.match(bounds_regex, key)
            if match:
                lowerbound = float(match.group(1))
                upperbound = float(match.group(2))
                self.model.add_feedback(StageFinalise.TAG, 'selective', str(upperbound))
                if score >= lowerbound and score <= upperbound:
                    self.model.add_feedback(StageFinalise.TAG,
                                            'selective',
                                            value)
                    return
    
        self.model.add_feedback(StageFinalise.TAG, 'selective', '')

    def set_value(self, stage_id, model_id, value):
        self.model.add_feedback(stage_id, model_id, value)
