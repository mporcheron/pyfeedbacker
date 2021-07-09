# -*- coding: utf-8 -*-

from . import base



class StagesMarks(base.StagesData):
    def __init__(self):
        super().__init__(Marks)

    def __dict__(self):
        marks = {}

        for key, value in self.items():
            marks[key] = value

        return marks



class Marks(base.Data):
    def __init__(self, outcome_id):
        super().__init__(outcome_id, None)
    
    def __iadd__(self, value):
        self.__setitem

    def __getitem__(self, outcome_id):
        outcome_id = str(outcome_id)
        return super().__getitem__(outcome_id)

    def __setitem__(self, outcome_id, mark):
        outcome_id = str(outcome_id)
        return super().__setitem__(outcome_id, mark)

    def __dict__(self):
        marks = {}

        for key, value in self.items():
            marks[key] = value

        return marks