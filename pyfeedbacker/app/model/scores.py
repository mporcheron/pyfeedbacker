# -*- coding: utf-8 -*-

from . import base
from .. import config



class StagesScores(base.StagesData):
    def __init__(self):
        super().__init__(Scores)

    sum = property(lambda self:self._calculate_score(), doc="""
            Read-only total score for the submission as a float.
            """)

    def __contains__(self, stage_id):
        return super().__contains__(stage_id)

    def _calculate_score(self):
        score = 0.0

        for value in self.values():
            score += value.sum

        s_max = config.ini[f'assessment'].getfloat('score_max', None)
        if s_max is not None and score > s_max:
            score = s_max

        s_min = config.ini[f'assessment'].getfloat('score_min', None)
        if s_min is not None and score < s_min:
            score = s_min

        return score

    def __float__(self):
        return self._calculate_score()

    def __int__(self):
        return int(self._calculate_score())



class Scores(base.Data):
    def __init__(self, stage_id):
        super().__init__(stage_id, 0.0)

    def __setitem__(self, score_id, value):
        return super().__setitem__(score_id, float(value))

    def __dict__(self):
        scores = {}

        for key, value in self.items():
            scores[key] = value

        return scores

    def __list__(self):
        scores = []

        for score in self.values():
            if len(indiv_feedback) > 0:
                scores.append(score)

        return scores

    sum = property(lambda self:self._calculate_score(), doc="""
            Read the total score for the submission as a float.
            """)

    def _calculate_score(self):
        score = 0.0

        for value in self.values():
            score += value

        s_max = config.ini[f'stage_{self.stage_id}'].getfloat('score_max', None)
        if s_max is not None and score > s_max:
            score = s_max

        s_min = config.ini[f'stage_{self.stage_id}'].getfloat('score_min', None)
        if s_min is not None and score < s_min:
            score = s_min

        return score

    def __float__(self):
        return self._calculate_score()

    def __int__(self):
        return int(self._calculate_score())