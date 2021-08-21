# -*- coding: utf-8 -*-

from pyfeedbacker.app import config
from pyfeedbacker.app.model import base



class FeedbackByStage(base.DataByStage):
    def __init__(self, root_model, parent_data_id):
        """Create a container for storing feedback for each stage in a 
        submission's scoring process.

        Outcomes is a four level model:
        Submission -> Stage -> Feedbacks -> Feedback
        
        Arguments:
        root_model -- The root model object.
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the submission identifier.
        """
        super().__init__(root_model,
                         child_data_type = Feedbacks,
                         parent_data_id  = parent_data_id)

        try:
            feedback_pre = config.ini['assessment'].get('feedback_pre', False)
            if feedback_pre:
                self['__init']['0'] = feedback_pre
        except:
            pass

    str = property(lambda self:self.__str__(), doc="""
            Retrieve a copy of the feedback as a new string.
            """)

    def __str__(self):
        """Retrieve all the feedback combined into a single string."""
        feedback = ''

        for stage_feedback in self.values():
            feedback += str(stage_feedback)
            feedback += '\n\n'

        return feedback



class Feedbacks(base.Data):
    def __init__(self, root_model, parent_data_id):
        """Feedback for a particular stage, organised by a unique feedback ID.
        
        Arguments:
        root_model -- The root model object.
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the stage identifier."""
        super().__init__(root_model,
                         child_data_type = str,
                         parent_data_id  = parent_data_id)

    stage_id = property(lambda self:self._parent_data_id, doc="""
            Retrieve the stage identifier.
            """)

    def __setitem__(self, feedback_id, value):
        """Set a piece of feedback, replacing \\n with \n (as caused by
        configparser in Python.
        
        Arguments:
        feedback_id -- A unique identifier for this piece of feedback.
        value -- A string giving feedback on the submission.
        """
        value = value.replace('\\n', '\n')
        return super().__setitem__(feedback_id, value)

    str = property(lambda self:self.__str__(), doc="""
            Retrieve a copy of the feedback as a new string.
            """)

    def __str__(self):
        """Retrieve all the feedback for this stage combined into a single
        string."""
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