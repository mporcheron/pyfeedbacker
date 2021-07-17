# -*- coding: utf-8 -*-

from . import base, scores
from .. import config



class StagesMarks(base.StagesData):
    def __init__(self):
        super().__init__(Marks)

    def __dict__(self):
        marks = {}

        for key, value in self.items():
            marks[key] = value

        return marks

    def __repr__(self):
        ret = 'StagesMarks('
        for key, value in self.items():
            ret += f'{key}: {value}, '
        ret += ')'

        return ret

    def sum(self, score_data):
        """
        Calculate the mark for all submissions or a single submission (depends
        on whether a StagesScores or Scores is passed in)
        """
        if isinstance(score_data, scores.Scores):
            return self[scores.stage_id].sum(scores)

        sum = 0.0

        for stage_id, scores_data in score_data.items():
            try:
                sum += self[stage_id].sum(scores_data)
            except TypeError:
                sum += scores_data.sum

        m_max = config.ini[f'assessment'].getfloat('mark_max', None)
        if m_max is not None and sum > m_max:
            sum = m_max

        m_min = config.ini[f'assessment'].getfloat('mark_min', None)
        if m_min is not None and sum < m_min:
            sum = m_min

        return sum



class Marks(base.Data):
    def __init__(self, outcome_id):
        super().__init__(outcome_id, None)

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

    def sum(self, scores):
        sum = 0.0

        for outcome_id, score in scores.items():
            try:
                try:
                    try:
                        key = str(score['key'])

                        # raise type error if self[outcome_id] is not a list
                        # raise KeyError if not in it
                        # raise ValueError if mark not set
                        key in self[outcome_id]
                        value = self[outcome_id][key]
                        sum += value
                    except TypeError:
                        if score['user_input']:
                            try:
                                sum += (score['value'] * self[outcome_id])
                            except TypeError:
                                # no weight set
                                sum += score['value']
                        else:
                            sum += self[outcome_id]
                except KeyError:
                    sum += score['value']
            except ValueError:
                try:
                    sum += score['value']
                except TypeError:
                    # may be a non-scored value
                    pass
            except TypeError:
                # no score
                pass

        m_max = config.ini[f'stage_{self.stage_id}'].getfloat('mark_max', None)
        if m_max is not None and sum > m_max:
            sum = m_max

        m_min = config.ini[f'stage_{self.stage_id}'].getfloat('mark_min', None)
        if m_min is not None and sum < m_min:
            sum = m_min

        return sum

    def __repr__(self):
        ret = '['
        for key, value in self.items():
            ret += f'({key}, {value}), '
        ret += ']'

        return ret