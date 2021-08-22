# -*- coding: utf-8 -*-

from pyfeedbacker.app import config
from pyfeedbacker.app.model import base



class OutcomesByStage(base.DataByStage):
    def __init__(self, root_model, parent_data_id):
        """Create a container for storing outcomes (i.e. scoring) for each stage in a submission's scoring process.

        Outcomes is a four level model:
        Submission -> Stage -> Outcomes -> Outcome
        
        Arguments:
        root_model -- The root model object.
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the submission identifier.
        """
        super().__init__(root_model = root_model,
                         child_data_type = Outcomes,
                         parent_data_id  = parent_data_id)

        try:
            score_init = config.ini['assessment'].getfloat('score_init', False)
            if score_init:
                self['__init']['0'] = Outcome(outcome_id = '0',
                                            value      = score_init)
        except KeyError:
            pass

    score = property(lambda self:self._calculate_score(), doc="""
            The total score for the submission as a float.
            """)

    mark = property(lambda self:self._calculate_mark(), doc="""
            The total mark for the submission as a float.
            """)

    def _calculate_score(self):
        """Calculate the total score for this submission, and apply any 
        configured min/max score bounds.
        """
        score = 0.0

        for value in self.values():
            score += value.score

        try:
            s_max = config.ini[f'assessment'].getfloat('score_max', None)
            if s_max is not None and score > s_max:
                score = s_max
        except KeyError:
            pass

        try:
            s_min = config.ini[f'assessment'].getfloat('score_min', None)
            if s_min is not None and score < s_min:
                score = s_min
        except KeyError:
            pass

        return score

    def _calculate_mark(self):
        """Calculate the total mark for this submission, and apply any 
        configured min/max sum bounds.
        """
        sum = 0.0

        for value in self.values():
            sum += value.mark

        try:
            m_max = config.ini[f'assessment'].getfloat('mark_max', None)
            if m_max is not None and sum > m_max:
                sum = m_max
        except KeyError:
            pass

        try:
            m_min = config.ini[f'assessment'].getfloat('mark_min', None)
            if m_min is not None and sum < m_min:
                sum = m_min
        except KeyError:
            pass

        return sum

    def __float__(self):
        """The total score for the submission as a float."""
        return self._calculate_score()



class Outcomes(base.Data):
    def __init__(self, root_model, parent_data_id):
        """Feedback for a particular stage, organised by a unique feedback ID.
        
        Arguments:
        root_model -- The root model object.
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the stage identifier."""
        super().__init__(root_model      = root_model,
                         child_data_type = Outcome,
                         parent_data_id  = parent_data_id)

    stage_id = property(lambda self:self._parent_data_id, doc="""
            Retrieve the stage identifier.
            """)

    def __setitem__(self, outcome_id, new_outcome):
        outcome_id = str(outcome_id)
        
        try:
            existing_index = list(self.values()).index(new_outcome)
            existing_key = list(self.keys())[existing_index]
            del self[existing_key]
        except:
            pass

        if outcome_id != new_outcome['outcome_id']:
            new_outcome['outcome_id'] = outcome_id

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

    score = property(lambda self:self._calculate_score(), doc="""
            Read the total score for the submission as a float.
            """)

    mark = property(lambda self:self._calculate_mark(), doc="""
            Read the total mark for the submission as a float.
            """)

    def _calculate_score(self):
        """Calculate the total score for a particular stage."""
        score = 0.0

        for outcome in self.values():
            try:
                score += outcome['value']
            except:
                pass

        try:
            s_max = config.ini[f'stage_{self.stage_id}'].getfloat(
                'score_max', None)
            if s_max is not None and score > s_max:
                score = s_max
        except KeyError:
            pass

        try:
            s_min = config.ini[f'stage_{self.stage_id}'].getfloat(
                'score_min', None)
            if s_min is not None and score < s_min:
                score = s_min
        except KeyError:
            pass

        return score

    def _calculate_mark(self):
        """Calculate the total mark for a particular stage."""
        try:
            marks = self._root_model.marks[self.stage_id]
        except:
            marks = None
        sum = 0.0

        for outcome_id, outcome in self.items():
            if outcome['user_input']:
                try:
                    # if this is user_input, any value in the marks model is 
                    # a scale factor
                    sum += (outcome['value'] * marks[outcome_id])
                except:
                    # if the value in the outcomes model is a float, add it
                    # otherwise do nothing
                    try:
                        sum += outcome['value']
                    except TypeError:
                        pass
            else:
                # if there is a value in the marks model for the outcome, use
                # that, otherwise use the score
                try:
                    key = str(outcome['key'])
                    value = marks[outcome_id][key]
                    sum += value
                except:
                    # if the value in the outcomes model is a float, add it
                    # otherwise do nothing
                    try:
                        sum += outcome['value']
                    except TypeError:
                        pass

        try:
            m_max = config.ini[f'stage_{self.stage_id}'].getfloat(
                'mark_max', None)
            if m_max is not None and sum > m_max:
                sum = m_max
        except KeyError:
            pass

        try:
            m_min = config.ini[f'stage_{self.stage_id}'].getfloat(
                'mark_min', None)
            if m_min is not None and sum < m_min:
                sum = m_min
        except KeyError:
            pass

        return sum

    def __float__(self):
        """Calculate the total score for a particular stage."""
        return self._calculate_score()




class Outcome(dict):
    def __init__(self,
                 outcome_id  = None,
                 key         = None,
                 explanation = None,
                 value       = None,
                 all_values  = None,
                 user_input  = False):
        super().__init__()

        self['outcome_id']  = outcome_id
        self['key']         = key
        self['explanation'] = explanation
        self['value']       = value
        self['all_values']  = all_values
        self['user_input']  = user_input

    def __setitem__(self, key, value):
        """Set an element in the outcome.
        
        Arguments:
        key -- A key for the element (see `__init__` parameters)
        value -- A value for the element. If the `key` is 'value', then this
            value is cast to a float.
        """
        key = str(key)
        if key == 'value':
            try:
                return super().__setitem__(key, float(value))
            except:
                pass

        super().__setitem__(key, value)

    def __float__(self):
        """Retrieve the value of the outcome as a float, or raise a 
        ValueError if there is no specific value specified.
        
        Raises:
        ValueError -- if no value is set for the outcom
        """
        try:
            return float(self['value'])
        except TypeError:
            outcome_id = self['outcome_id']
            raise ValueError(f'Value is not set for outcome {outcome_id}')

    def __repr__(self):
        return str(f'Outcome({self.outcome_id}, {self.value})')