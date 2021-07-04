# -*- coding: utf-8 -*-

from . import controller
from .. import config, stage
from ..view import urwid as view

from collections import OrderedDict

import abc
import importlib
import os
import sys
import threading



class Controller(controller.BaseController):

    def __init__(self, submission):
        """
        Controller for marking a submission by a student and generating scores
        and feedback, separated by 'stages'.
        """
        super().__init__()

        self.submission      = submission

    def set_model(self, model):
        """
        Set the model that'll store information about a submission
        and then store scores/marks and feedback.
        """
        super().set_model(model)
        self.scores    = model['scores'][self.submission]
        self.feedbacks = model['feedbacks'][self.submission]
        self.outcomes  = model['outcomes'][self.submission]
        return self

    def execute_first_stage(self):
        if self._next_stage_id is not None:
            return

        if self.scores.sum != 0.0 or len(self.feedbacks.str) > 0:
            self.view.show_alert('This submission has already been marked',
                                 'Do you want to keep the existing marking' +
                                 '\n or would you like to start again?',
                                 view.UrwidView.ALERT_YESNO,
                                 self._on_keep_existing_scores_response,
                                 ['Keep existing scores', 'Start again'])
        else:
            self._execute_first_stage()

    def _on_keep_existing_scores_response(self, response):
        if response == 'Start again':
            self.scores.clear()
            self.feedbacks.clear()
            self.outcomes.clear()

        self._execute_first_stage()

    def _execute_first_stage(self):
        self._next_stage_id = self.stages_ids[0]
        self.execute_stage(self._next_stage_id)

    def add_score(self, stage_id, score_id, value):
        self.scores[stage_id][score_id] = value
        self.view.set_score(self.scores.sum)

    def add_feedback(self, stage_id, feedback_id, value):
        self.feedbacks[stage_id][feedback_id] = value

    def set_outcome(self, stage_id, outcome_id, outcome):
        self.outcomes[stage_id][outcome_id] = outcome

    def execute_stage(self, stage_id=None):
        """
        Execute a stage if it hasn't been executed yet and is ready for
        execution.
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
            self.add_feedback(stage_id, '__pre', stage_info.feedback_pre)

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
                self.add_feedback(stage_id, '__post', feedback_post)
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
        result = instance.run()
        if result:
            try:
                self.report(result)
            except stage.StageError as se:
                self.view.show_alert('Error', str(se))

    def refresh_stage(self, stage_id):
        if stage_id not in self.stages_handlers:
            raise stage.StageIgnorableError('Stage has not yet executed.')

        instance = self.stages_handlers[stage_id]
        instance.refresh()
        self.set_stage_output(stage_id, instance.output)

    def report(self, result, stage_id=None, stage_info=None):
        """Report a stage result to the UI"""
        if stage_id is None or stage_info is None:
            stage_id   = self.current_stage[0]
            stage_info = self.current_stage[1]

        if result.score is not None:
            self.add_score(stage_id, 'reported', result.score)

        if result.outcome is not None:
            self.set_outcome(stage_id, 'reported', result.outcome)

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
            self.add_feedeback(stage_id, '__post', feedback_post)

