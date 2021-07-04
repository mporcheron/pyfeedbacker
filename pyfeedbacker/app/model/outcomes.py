# -*- coding: utf-8 -*-

from . import base



class StagesOutcomes(base.StagesData):
    def __init__(self):
        super().__init__(Outcomes)



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

    def __setitem__(self, outcome_id, outcome):
        outcome_id = str(outcome_id)
        return super().__setitem__(outcome_id, outcome)

    def add(self, key, explanation, score):
        self[key] = Outcome(key, explanation, score)

    def __dict__(self):
        outcomes = {}

        for key, value in self.items():
            outcomes[key] = value

        return outcomes




class Outcome(dict):
    def __init__(self, key=None, explanation=None, value=None):
        super().__init__()

        self['key']         = key
        self['explanation'] = explanation
        self['value']       = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return super().__getattr__(key)

    def __setattr__(self, key, value):
        pass

    def __repr__(self):
        return str(f'Outcome({self.key}, {self.value})')