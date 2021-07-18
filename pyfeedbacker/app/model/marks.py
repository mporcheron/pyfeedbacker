# -*- coding: utf-8 -*-

from pyfeedbacker.app import config
from pyfeedbacker.app.model import base



class StagesMarks(base.DataByStage):
    def __init__(self):
        """Create a container for storing marks (i.e. final mark) for each stage in a submission's scoring process.

        Marks is a three level model:
        Stage -> Marks -> float OR dict (str->float)
        """
        super().__init__(child_data_type = Marks,
                         parent_data_id  = None)

    def sum(self, outcomes_for_submission):
        """Calculate the mark for a submission by passing in an outcomes model of its scores. Applies any mix/max mark rules specified in the 
        configuration.

        Arguments:
        outcomes_for_submission -- An object containing a single submission's
            outcomes
        """
        sum = 0.0

        for stage_id, scores_data in outcomes_for_submission.items():
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
    def __init__(self, parent_data_id):
        """Marks for a particular stage's outcomes, organise by the outcome 
        identifier.
        
        Arguments:
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the stage identifier."""
        super().__init__(child_data_type = None,
                         parent_data_id  = parent_data_id)

        self.stage_id = parent_data_id

    def sum(self, outcomes_for_stage):
        """Calculate the mark for a stage by passing in an outcomes model of its scores. Applies any mix/max mark rules specified in the 
        configuration.

        Arguments:
        outcomes_for_stage -- An object containing a single submission's
            outcomes for a specific stage
        """
        sum = 0.0

        for outcome_id, outcome in outcomes_for_stage.items():
            try:
                try:
                    try:
                        key = str(outcome['key'])

                        # raise type error if self[outcome_id] is not a list
                        # raise KeyError if not in it
                        # raise ValueError if mark not set
                        value = self[outcome_id][key]
                        sum += value
                    except TypeError:
                        if outcome['user_input']:
                            try:
                                sum += (outcome['value'] * self[outcome_id])
                            except TypeError:
                                # no weight set
                                sum += outcome['value']
                        else:
                            sum += self[outcome_id]
                except KeyError:
                    sum += outcome['value']
            except ValueError:
                try:
                    sum += outcome['value']
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