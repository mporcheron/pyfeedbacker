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
        if outcome_id in self:
            new_outcome = self[outcome_id]
            if outcome['outcome_id']:
                new_outcome['outcome_id'] = outcome['outcome_id']
            if outcome['key']:
                new_outcome['key'] = outcome['key']
            if outcome['explanation']:
                new_outcome['explanation'] = outcome['explanation']
            if outcome['value']:
                new_outcome['value'] = outcome['value']
            if outcome['all_values']:
                new_outcome['all_values'] = outcome['all_values']
        else:
            outcome['outcome_id'] = outcome_id
            return super().__setitem__(outcome_id, outcome)

    def add(self, outcome_id, key, explanation, score):
        self.__setitem__(outcome_id, Outcome(key, explanation, score))

    def __dict__(self):
        outcomes = {}

        for key, value in self.items():
            outcomes[key] = value

        return outcomes




class Outcome(dict):
    def __init__(self,
                 outcome_id=None,
                 key=None,
                 explanation=None,
                 value=None,
                 all_values=None):
        super().__init__()

        self['outcome_id']  = outcome_id
        self['key']         = key
        self['explanation'] = explanation
        self['value']       = value
        self['all_values']  = all_values

    def __getattr__(self, key):
        key = str(key)
        try:
            return super().__getitem__(key)
        except KeyError:
            return super().__getattr__(key)

    def __setattr__(self, key, value):
        pass

    def __repr__(self):
        return str(f'Outcome({self.key}, {self.value})')