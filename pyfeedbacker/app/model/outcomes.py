# -*- coding: utf-8 -*-

from .. import config
from . import base



class StagesOutcomes(base.StagesData):
    def __init__(self):
        super().__init__(Outcomes)

        score_init = config.ini['assessment'].getfloat('score_init', False)
        if score_init:
            self['__init']['0'] = Outcome(outcome_id = '0',
                                          value      = score_init)

    sum = property(lambda self:self._calculate_score(), doc="""
            Read-only total score for the submission as a float.
            """)

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



class Outcomes(base.Data):
    def __init__(self, stage_id):
        super().__init__(stage_id, None)

    score_min = property(lambda self:min(self.values(),
                                         key=lambda outcome: outcome.score),
        doc="""
            Read-only minimum score in the outcomes.
            """)

    score_max = property(lambda self:min(self.values(),
                                         key=lambda outcome: outcome.score),
        doc="""
            Read-only minimum score in the outcomes.
            """)

    def __getitem__(self, outcome_id):
        outcome_id = str(outcome_id)
        return super().__getitem__(outcome_id)

    def __setitem__(self, outcome_id, new_outcome):
        outcome_id = str(outcome_id)
        if outcome_id in self:
            outcome = self[outcome_id]
            if new_outcome['outcome_id'] != outcome['outcome_id']:
                outcome['outcome_id'] = new_outcome['outcome_id']

            if new_outcome['key'] != outcome['key']:
                outcome['key'] = new_outcome['key']

            if new_outcome['explanation'] != outcome['explanation']:
                outcome['explanation'] = new_outcome['explanation']

            if new_outcome['value'] != outcome['value']:
                outcome['value'] = new_outcome['value']

            if new_outcome['all_values'] != outcome['all_values']:
                outcome['all_values'] = new_outcome['all_values']
        else:
            new_outcome['outcome_id'] = outcome_id
            return super().__setitem__(outcome_id, new_outcome)

    def add(self, outcome_id, key, explanation, score):
        self.__setitem__(outcome_id, Outcome(key, explanation, score))

    def __dict__(self):
        outcomes = {}

        for key, value in self.items():
            outcomes[key] = value

        return outcomes

    sum = property(lambda self:self._calculate_score(), doc="""
            Read the total score for the submission as a float.
            """)

    def _calculate_score(self):
        score = 0.0

        for outcome in self.values():
            try:
                score += outcome['value']
            except:
                pass

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




class Outcome(dict):
    def __init__(self,
                 outcome_id  = None,
                 key         = None,
                 explanation = None,
                 value       = None,
                 all_values  = None):
        super().__init__()

        self['outcome_id']  = outcome_id
        self['key']         = key
        self['explanation'] = explanation
        self['value']       = value
        self['all_values']  = all_values

    def __getitem__(self, key):
        key = str(key)
        return super().__getitem__(str(key))

    def __setitem__(self, key, value):
        key = str(key)
        if key == 'value':
            try:
                super().__setitem__(key, float(value))
            except:
                super().__setitem__(key, None)
        else:
            super().__setitem__(key, value)

    def __float__(self):
        try:
            return float(self['value'])
        except ValueError:
            return None

    def __repr__(self):
        return str(f'Outcome({self.key}, {self.value})')