# -*- coding: utf-8 -*-

from .. import config
from . import scores, feedbacks, outcomes

from collections import OrderedDict

import abc



class BaseModel(object):
    def __init__(self):
        """
        All class and feedback should be stored in a storage model of some
        form
        """
        self._scores    = AllSubmissions(scores.StagesScores)
        self._feedbacks = AllSubmissions(feedbacks.StagesFeedback)
        self._outcomes  = AllSubmissions(outcomes.StagesOutcomes)

        self._set_init_data()

    def __getitem__(self, type):
        if type == 'scores':
            return self._scores
        elif type == 'feedbacks':
            return self._feedbacks
        elif type == 'outcomes':
            return self._outcomes
        else:
            raise KeyError(f'Unknown model data type: f{type}')

    def _set_init_data(self):
        score_init = config.ini['assessment'].getfloat('score_init', None)
        if score_init:
            self['scores']['0'].append('0', score_init)

        feedback_pre = config.ini['assessment'].get('feedback_pre', None)
        if feedback_pre:
            self['feedback']['0'].append('0', feedback_pre)

    @abc.abstractmethod
    def save(self):
        pass

    def calculate_stage_score(self, stage_id):
        score = 0.0
        if stage_id in self['scores']:
            scores = self['scores'][stage_id]

            for this_score in scores.values():
                if this_score:
                    score += float(this_score)

        s_max = config.ini[f'stage_{stage_id}'].getfloat('score_max', None)
        if s_max is not None and score > s_max:
            score = s_max

        s_min = config.ini[f'stage_{stage_id}'].getfloat('score_min', None)
        if s_min is not None and score < s_min:
            score = s_min

        return score

    def calculate_score(self):
        score = 0

        raw_scores = self['scores']
        for stage_id in raw_scores.keys():
            score += self.__getattribute__(f'score_{stage_id}')

        s_max = config.ini[f'assessment'].getfloat('score_max', None)
        if s_max is not None and score > s_max:
            score = s_max

        s_min = config.ini[f'assessment'].getfloat('score_min', None)
        if s_min is not None and score < s_min:
            score = s_min

        return score



class AllSubmissions(OrderedDict):
    def __init__(self, model_type):
        self._model_type = model_type

    def __getitem__(self, submission):
        submission = str(submission)
        try:
            return super().__getitem__(submission)
        except KeyError:
            super().__setitem__(submission, self._model_type())
            return super().__getitem__(submission)

    def __contains__(self, submission):
        submission = str(submission)
        try:
            return super().__contains__(submission)
        except KeyError:
            return False

    dict = property(lambda self:self.__dict__(), doc="""
            Get a copy of the data as a dictionary.
            """)

    def __dict__(self):
        items = {}

        for key, value in self.items():
            items[key] = value.dict

        return items