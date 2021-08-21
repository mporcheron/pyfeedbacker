# -*- coding: utf-8 -*-

from pyfeedbacker.app import config
from pyfeedbacker.app.model import base



class StagesMarks(base.DataByStage):
    def __init__(self, root_model):
        """Create a container for storing marks (i.e. final mark) for each stage in a submission's scoring process.

        Marks is a three level model:
        Stage -> Marks -> float OR dict (str->float)
        """
        super().__init__(root_model      = root_model,
                         child_data_type = Marks,
                         parent_data_id  = None)


class Marks(base.Data):
    def __init__(self, root_model, parent_data_id):
        """Marks for a particular stage's outcomes, organise by the outcome 
        identifier.
        
        Arguments:
        root_model -- The root model object.
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the stage identifier."""
        super().__init__(root_model      = root_model,
                         child_data_type = None,
                         parent_data_id  = parent_data_id)

    stage_id = property(lambda self:self._parent_data_id, doc="""
            Retrieve the stage identifier.
            """)