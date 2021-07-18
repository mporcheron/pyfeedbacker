# -*- coding: utf-8 -*-

from pyfeedbacker.app.model import feedbacks, outcomes, marks

from collections import OrderedDict

import abc



class Model(object):
    def __init__(self):
        """All data corresponding to submissions is stored within this class
        instance.

        There are three main models:
        1. Outcomes model, which stores data corresponding to scoring, and which
           may or may not be the final mark for a student depending on 
           program configuration. This is organised by submission.
        2. Feedbacks model, which stores feedback to be given to the student, 
           organised by submission.
        3. Marks model, which stores the marks for each component
        """
        self.outcomes  = AllSubmissions(outcomes.OutcomesByStage)
        self.feedbacks = AllSubmissions(feedbacks.FeedbackByStage)
        self.marks     = marks.StagesMarks()

    @abc.abstractmethod
    def save(self):
        """Save the model data to permanent storage."""
        pass



class AllSubmissions(OrderedDict):
    def __init__(self, model_type):
        """Models which store data by submission have an AllSubmissions
        object as the root storge container.
        
        Arguments:
        model_type -- A data type that will be stored in this object, one for
            each submission.
        """
        self._model_type = model_type

    def __getitem__(self, submission):
        """Retrieve an item using the square bracket syntax. If a particular 
        `submission` doesn't exist, then one will be created with an initialised
        value of the type passed into `__init__`.

        Arguments:
        stage_id -- Identifier of the stage, will be converted to a string if it
            isn't already a string.
        """
        submission = str(submission)
        try:
            return super().__getitem__(submission)
        except KeyError:
            super().__setitem__(submission, self._model_type(submission))
            return super().__getitem__(submission)

    def __contains__(self, submission):
        submission = str(submission)
        try:
            return super().__contains__(submission)
        except KeyError:
            return False

    dict = property(lambda self:self.__dict__(), doc="""
            Retrieve a copy of the data as a new dictionary.
            """)

    def __dict__(self):
        items = {}

        for key, value in self.items():
            items[key] = value.dict

        return items

    def __repr__(self):
        # ret = '{' + self.submission + ': {'
        # for key, value in self.items():
        #     ret += f'{key}: {value}, '
        # ret += '\})'

        return 'ffff'

    def __repr__(self):
        ret  = f'{self.__class__}('
        ret += str(list(self))
        ret += ')'

        return ret

    def __str__(self):
        return self.__repr__()