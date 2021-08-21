# -*- coding: utf-8 -*-

from pyfeedbacker.app import stage
from pyfeedbacker.app.view import urwid as view
from pyfeedbacker.app.controller import base

import threading



class Controller(base.BaseController):
    def __init__(self, submission):
        """Controller for scoring a submission by a student and generating scores and feedback, separated by 'stages'.
        """
        super().__init__()

        self.submission      = submission

    def set_model(self, model):
        """Set the model that'll store information about a submission
        and then store outcomes from the scoring and feedback for the
        submission.

        Arguments:
        model -- Root model.
        """
        super().set_model(model)

        self.feedbacks = model.feedbacks[self.submission]
        self.outcomes  = model.outcomes[self.submission]

        return self

    def execute_first_stage(self):
        """Execute the first stage in the list. This is the callback function
        from the UI, which the UI should trigger when it has loaded.

        If the user is runnign the scorer application for a submission that has
        already been scored, instead of the stage being executed, they'll be
        given a prompt asking whether they want to continue with the existing
        scores or start again.
        """
        self.view.set_score(self.outcomes.score)

        if self._next_stage_id is not None:
            return

        if self.outcomes.score != 0.0 or len(self.feedbacks.str) > 0:
            self.view.show_alert('This submission has already been marked',
                                 'Do you want to keep the existing marking' +
                                 '\n or would you like to start again?',
                                 view.UrwidView.ALERT_YESNO,
                                 self._on_keep_existing_scores_response,
                                 ['Keep existing scores', 'Start again'])
        else:
            self._execute_first_stage()

    def _on_keep_existing_scores_response(self, response):
        """Callback function on when the user runs the scorer application
        for a submission that already has scores in the model.
        
        This will execute the first stage.

        Arguments:
        response -- Text of the button label selected by the user.
        """
        if response == 'Start again':
            self.feedbacks.clear()
            self.outcomes.clear()

        self._execute_first_stage()

    def _execute_first_stage(self):
        """Execute the first stage in the application."""
        self._next_stage_id = self.stages_ids[0]
        self.execute_stage(self._next_stage_id)

    def set_feedback(self, stage_id, feedback_id, value):
        """Set a feedback value in the model.
        
        Arguments:
        stage_id -- The stage identifier for the feedback.
        feedback_id -- An identifier for the feedback that is unique per stage.
        value -- A string value of the feedback.
        """
        self.feedbacks[stage_id][feedback_id] = value

    def set_outcome(self, stage_id, outcome_id, outcome):
        """Set an outcome value in the model.
        
        Arguments:
        stage_id -- The stage identifier for the outcome.
        outcome_id -- An identifier for the outcome that is unique per stage.
        outcome -- Outcome object to save to the model.
        """
        self.outcomes[stage_id][outcome_id] = outcome

        self.view.set_score(self.outcomes.score)

    def select_stage(self, stage_id):
        """Select a stage and:
        1) if it hasn't been executed, and
        2) everything before it has been executed
        then it will be executed
        
        Keyword arguments:
        stage_id -- Stage to show and maybe execute.
        """
        stage_info = self.stages[stage_id]

        if self._next_stage_id == stage_id:
            self.view.show_stage(stage_id, stage_info.label)
            self.execute_stage(stage_id)
        else:
            try:
                self.refresh_stage(stage_id)
            except stage.StageIgnorableError:
                pass
            self.view.show_stage(stage_id, stage_info.label)

    def execute_stage(self, stage_id = None):
        """Execute a stage if it hasn't been executed yet.
        
        Keyword arguments:
        stage_id -- Stage to execute, or the next valid stage if None is 
            provided
        """
        if stage_id not in self.stages:
            raise stage.StageError(f'The id {stage_id} does not correspond to' +
                                   ' an expected stage')

        if self._next_stage_id is not stage_id:
            raise stage.StageError(f'The stage {stage_id} is not ready for ' +
                                   'execution')

        self._next_stage_id = None

        list_stages_info = list(self.stages.items())
        stage_info       = self.stages[stage_id]

        # don't do anything if the stage has failed
        if stage_info.state is stage.StageInfo.STATE_FAILED:
            return

        # is the stage inactive? (i.e., not yet executed but can…)
        if stage_info.state is not stage.StageInfo.STATE_INACTIVE:
            return

        # add feedback
        if stage_info.feedback_pre is not None:
            self.set_feedback(stage_id, '__pre', stage_info.feedback_pre)

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

        # execute the stage
        if isinstance(instance, stage.HandlerNone):
            state = stage.StageInfo.STATE_COMPLETE
            self.view.set_stage_state(self.current_stage[0], state)

            next_stage_id = self.get_next_stage_id(stage_id)
            next_stage    = self.stages[next_stage_id]

            if next_stage.state == stage.StageInfo.STATE_INACTIVE:
                self._next_stage_id = next_stage_id

            if self.progress_on_success:
                self.execute_stage(next_stage_id)

            # add post feedback for None as report() is never called
            feedback_post = stage_info.feedback_post
            if feedback_post is not None and len(feedback_post.strip()) > 0:
                self.set_feedback(stage_id, '__post', feedback_post)
        elif isinstance(instance, stage.HandlerForm):
            state = stage.StageInfo.STATE_ACTIVE
            self.view.set_stage_state(self.current_stage[0], state)
            self.set_stage_output(self.current_stage[0], instance.output)
        else:
            state  = stage.StageInfo.STATE_ACTIVE
            self.view.set_stage_state(self.current_stage[0], state)

            thread = threading.Thread(target = self._execute_stage,
                                      args   = [instance])
            thread.daemon = True
            self._a_stage_is_active = True
            thread.start()

    def _execute_stage(self, instance):
        """Function to execute a stage that should be called from a background
        thread.
        
        Arguments:
        instance -- Subclass of HandlerBase that contains the main code for the
            stage.
        """
        result = instance.run()
        if result:
            try:
                self.report(result)
            except stage.StageError as se:
                self.view.show_alert('Error', str(se))

    def refresh_stage(self, stage_id):
        """Refresh a stage's output.
        
        Arguments:
        stage_id -- Stage to request to provide an updated output.
            provided
        """
        if stage_id not in self.stages_handlers:
            raise stage.StageIgnorableError('Stage has not yet executed.')

        instance = self.stages_handlers[stage_id]
        instance.refresh()
        self.set_stage_output(stage_id, instance.output)

    def report(self, result, stage_id=None, stage_info=None):
        """Handle the report generated when a stage completes execution and 
        process it.

        If auto progression is enabled, the next stage will then be selected.
        
        Arguments:
        result -- A StageResult instance.
        
        Keyword arguments:
        stage_id -- Stage providing the report, if one isn't provided it is
            assumed to be the current stage.
        stage_info -- Stage info object for the stage providing the report,
            one will be retrieved for the current stage if one isn't provided.
            provided
        """
        if stage_id is None or stage_info is None:
            stage_id   = self.current_stage[0]
            stage_info = self.current_stage[1]

        if result.outcome:
            self.set_outcome(
                stage_id,
                result.outcome['outcome_id'],
                result.outcome)

        if result.result == stage.StageResult.RESULT_PASS or \
                result.result == stage.StageResult.RESULT_PASS_NONFINAL:
            state = stage.StageInfo.STATE_COMPLETE
            self.view.set_stage_state(stage_id, state)

            if result.output is not None:
                self.set_stage_output(stage_id, result.output)
            try:
                next_stage_id = self.get_next_stage_id(stage_id)
                next_stage    = self.stages[next_stage_id]

                if next_stage.state == stage.StageInfo.STATE_INACTIVE:
                    self._next_stage_id = next_stage_id

                if result.result == stage.StageResult.RESULT_PASS and \
                        self.progress_on_success:
                    self.execute_stage(next_stage_id)
            except KeyError:
                pass

        elif result.result == stage.StageResult.RESULT_PARTIAL:
            state = stage.StageInfo.STATE_COMPLETE
            self.view.set_stage_state(stage_id, state)
            self.set_stage_output(stage_id, result.output)

        else:
            state  = stage.StageInfo.STATE_FAILED

            if stage_info.halt_on_error:
                for _, stage_ in self.stages.items():
                    stage_.set_state(stage.StageInfo.STATE_FAILED)

            self.view.set_stage_state(self.current_stage[0], state)
            self.set_stage_output(self.current_stage[0], result.output)

            self.view.show_alert(stage_info.label,
                                 result.error,
                                 stage_info.halt_on_error)

        feedback_post = stage_info.feedback_post
        if feedback_post is not None and len(feedback_post.strip()) > 0:
            self.set_feedback(stage_id, '__post', feedback_post)

