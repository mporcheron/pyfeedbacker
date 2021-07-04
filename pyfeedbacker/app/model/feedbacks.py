# -*- coding: utf-8 -*-

from . import base



class StagesFeedback(base.StagesData):
    def __init__(self):
        super().__init__(Feedbacks)

    def __str__(self):
        feedback = ''
        for stage_feedback in self.values():
            feedback += str(stage_feedback)
            feedback += '\n\n'

        return feedback



class Feedbacks(base.Data):
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