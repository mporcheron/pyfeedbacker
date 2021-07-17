# -*- coding: utf-8 -*-

from . import controller
from .. import stage



class Controller(controller.BaseController):
    def __init__(self):
        """Controller for creating marks for all the submission components, and 
        thus each submission's mark. Generates final feedback too.
        """
        super().__init__()

    def set_model(self, model):
        """Set the model that'll store information about all submissions.
        """
        super().set_model(model)

        self.marks     = model.marks
        self.outcomes  = model.outcomes

        return self

    def set_view(self, model):
        """Set the view that will handle the entire interface for the
        application.
        """
        super().set_view(model)
        self.view.update_marks()
        return self

    def _create_marks_model_scale(self, stage_id, outcome_id, outcome):
        """Populate the marks model for a specific outcome that is a question 
        where there is a range of possible values/scores awarded per
        submission. Takes the outcome and populates the marks model. If the 
        marks model has a value in it for the model, this is not overwritten.

        The outcome does not need to be from the outcomes model as the `value`
        is ignored-instead, it can come from the stages.

        Arguments:
        stage_id -- The stage identifier for the outcome.
        outcome_id -- The unique outcome identifier.
        outcome -- An outcome object containing an `all_values` value, which is 
            a list of (str, float)
        """
        for mark_id, value in enumerate(outcome['all_values']):
            mark_id = str(mark_id)
            mark    = value[1]

            try:
                model_value = self.marks[stage_id][outcome_id][mark_id]

                if model_value is not None:
                    continue

                self.marks[stage_id][outcome_id][mark_id] = mark
            except KeyError:
                self.marks[stage_id][outcome_id][mark_id] = mark
            except TypeError:
                self.marks[stage_id][outcome_id] = {mark_id: mark}

    def _create_marks_model_single(self, stage_id, outcome_id, outcome):
        """Populate the marks model for a specific outcome that is a question 
        where there is only one values/score awarded per submission. Takes the 
        outcome and populates the marks model. If the marks model has a value 
        in it for the model, this is not overwritten.

        The outcome does not need to be from the outcomes model as the `value`
        is ignored-instead, it can come from the stages.

        Arguments:
        stage_id -- The stage identifier for the outcome.
        outcome_id -- The unique outcome identifier.
        outcome -- An outcome object containing an `all_values` value, which is 
            a list of (str, float)
        """
        if outcome['user_input']:
            # user inputs are scaled, so have a factor/value of 1.0
            mark = 1.0
        else:
            mark = outcome['value']

        model_value = self.marks[stage_id][outcome_id]

        if model_value is not None:
            return

        self.marks[stage_id][outcome_id] = mark

    def set_mark(self, stage_id, outcome_id, mark_id, mark):
        """Set a mark in the marks model.

        Arguments:
        stage_id -- The stage identifier for the outcome.
        outcome_id -- The unique outcome identifier.
        mark_id -- The unique identifier for the mark (only used in questions 
            where there are a range of possible values, set to None otherwise)
        mark -- The mark to award.
        """
        mark_id = str(mark_id)
        if mark_id is None:
            self.model.marks[stage_id][outcome_id] = mark
        else:
            try:
                self.model.marks[stage_id][outcome_id][mark_id] = mark
            except TypeError:
                # mark_id is invalid type (likely None)
                self.model.marks[stage_id][outcome_id] = mark
            except AttributeError:
                # mark_id doesn't exist
                self.model.marks[stage_id][outcome_id] = {}
                self.model.marks[stage_id][outcome_id][mark_id] = mark

        self.view.update_marks()

    def execute_first_stage(self):
        """Execute the first stage in the list. This is the callback function
        from the UI, which the UI should trigger when it has loaded.
        """
        if self._next_stage_id is not None:
            return

        self.execute_stage(self.stages_ids[0])

    def select_stage(self, stage_id):
        """Select a stage, updating the UI, and then execute it.

        Arguments:
        stage_id -- Stage identifier of the stage to execute.
        """
        stage_info = self.stages[stage_id]
        self.view.show_stage(stage_id, stage_info.label)
        self.execute_stage(stage_id)

    def execute_stage(self, stage_id=None):
        """Execute a stage if it hasn't been executed yet.
        
        Keyword arguments:
        stage_id -- Stage to execute, or the next valid stage if None is 
            provided
        """
        if stage_id not in self.stages:
            raise stage.StageError(f'The id {stage_id} does not correspond to' +
                                   ' an expected stage')

        list_stages_info = list(self.stages.items())
        stage_info       = self.stages[stage_id]

        # retrieve the handler
        self.current_stage = (stage_id, stage_info)
        state = stage.StageInfo.STATE_ACTIVE

        self.view.show_stage(stage_id, stage_info.label)

        instance = None
        try:
            instance = stage_info.handler(stage_id)
            instance.set_framework(self)

            self.stages_handlers[stage_id] = instance
        except Exception as e:
            result = stage.StageResult(stage.StageResult.RESULT_CRITICAL)
            result.set_error('Failed to start stage handler: ' + str(e))
            self.report(result)
            if self.debug:
                raise e
            return

        # create/refresh marks model
        for outcome_id, outcome in instance.outcomes.items():
            # is scale question or not
            if outcome['all_values'] is None:
                self._create_marks_model_single(stage_id,
                                                outcome_id,
                                                outcome)
            else:
                self._create_marks_model_scale(stage_id,
                                                outcome_id,
                                                outcome)

        output = stage.OutputMarker(self.model, stage_id, instance.outcomes)

        self.view.set_stage_state(stage_id, stage.StageInfo.STATE_COMPLETE)
        self.set_stage_output(self.current_stage[0], output)

    def save_and_close(self):
        """Save the model to permanent storage and close the application.
        
        Ensures marks are saved.
        """
        self.model.save(True)
        self.view.quit()
