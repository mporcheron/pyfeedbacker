# -*- coding: utf-8 -*-

from .. import config
from .. import stage
from . import outcomes

from collections import OrderedDict

import abc
import csv



class BaseModel(object):
    def __init__(self):
        """
        All class and feedback should be stored in a storage model of some
        form
        """
        self._scores    = AllSubmissions(StagesScores)
        self._feedbacks = AllSubmissions(StagesFeedback)
        self._outcomes  = AllSubmissions(StagesOutcomes)

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




class StagesData(OrderedDict):
    def __init__(self, data_type):
        """
        Base class for storing all the data for a stage in the model. Its
        expected that any specific data type will extended this class and
        provide the data container type through calling __init__ on super()
        """
        self._data_type = data_type

    def __getitem__(self, stage_id):
        stage_id = str(stage_id)
        try:
            return super().__getitem__(stage_id)
        except KeyError:
            super().__setitem__(stage_id, self._data_type(stage_id))
            return super().__getitem__(stage_id)

    def __contains__(self, stage_id):
        stage_id = str(stage_id)
        try:
            return super().__contains__(stage_id)
        except KeyError:
            return False

    list = property(lambda self:self.__list__(), doc="""
            Get a copy of the data as a list.
            """)

    def _get_as_list(self):
        items = []

        for value in self.values():
            items += value.list

        return items

    def __list__(self):
        return self._get_as_list()

    dict = property(lambda self:self.__dict__(), doc="""
            Get a copy of the data as a dictionary.
            """)

    def __dict__(self):
        items = {}

        for key, value in self.items():
            items[key] = value.dict

        return items



class StagesScores(StagesData):
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



class StagesFeedback(StagesData):
    def __init__(self):
        super().__init__(Feedbacks)

    def __str__(self):
        feedback = ''
        for stage_feedback in self.values():
            feedback += str(stage_feedback)
            feedback += '\n\n'

        return feedback



class StagesOutcomes(StagesData):
    def __init__(self):
        super().__init__(outcomes.Outcomes)



class Data(OrderedDict):
    def __init__(self, stage_id, init_value):
        """
        Base data class for the model. Its expected that any specific data
        type will extended this class and provide an initial/default value
        through calling __init__ on super()
        """
        self.stage_id   = stage_id
        self.init_value = init_value

    def __getitem__(self, data_id):
        data_id = str(data_id)
        try:
            return super().__getitem__(data_id)
        except KeyError:
            super().__setitem__(data_id, self.init_value)
            return super().__getitem__(data_id)

    def __setitem__(self, data_id, value):
        data_id = str(data_id)
        return super().__setitem__(data_id, value)

    def __contains__(self, data_id):
        data_id = str(data_id)
        try:
            return super().__contains__(data_id)
        except KeyError:
            return False

    list = property(lambda self:self.__list__(), doc="""
            Return the data as a list.
            """)

    @abc.abstractmethod
    def __list__(self):
        pass

    dict = property(lambda self:self.__dict__(), doc="""
            Return the feedbacks as a dict.
            """)

    @abc.abstractmethod
    def __dict__(self):
        pass



class Scores(Data):
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



class Feedbacks(Data):
    def __init__(self, stage_id):
        super().__init__(stage_id, '')

    def __setitem__(self, feedback_id, value):
        value = value.replace('\\n', '\n')
        return super().__setitem__(feedback_id, value)

    def __dict__(self):
        feedbacks = {}

        for key, value in self.items():
            value = value.strip(' ')
            feedbacks[key] = value.replace('\\n', '\n')

        return feedbacks

    def __list__(self):
        feedbacks = []

        for indiv_feedback in self.values():
            indiv_feedback = indiv_feedback.strip(' ').replace('\\n', '\n')
            if len(indiv_feedback) > 0:
                feedbacks.append(indiv_feedback)

        return feedbacks

    def __str__(self):
        feedback = ''

        for indiv_feedback in self.values():
            indiv_feedback = indiv_feedback.strip(' ').replace('\\n', '\n')
            feedback += indiv_feedback

            try:
                if indiv_feedback[-1] != '\n' and \
                       indiv_feedback[-1] != '\t':
                    feedback += ' '
            except IndexError:
                pass

        return feedback