# -*- coding: utf-8 -*-

from . import base



class StagesWeights(base.StagesData):
    def __init__(self):
        super().__init__(Weights)

    def __dict__(self):
        weights = {}

        for key, value in self.items():
            weights[key] = value

        return weights



class Weights(base.Data):
    def __init__(self, outcome_id):
        super().__init__(outcome_id, None)
    
    def __iadd__(self, value):
        self.__setitem

    def __getitem__(self, outcome_id):
        outcome_id = str(outcome_id)
        return super().__getitem__(outcome_id)

    def __setitem__(self, outcome_id, weight):
        outcome_id = str(outcome_id)
        return super().__setitem__(outcome_id, weight)

    def __dict__(self):
        weights = {}

        for key, value in self.items():
            weights[key] = value

        return weights