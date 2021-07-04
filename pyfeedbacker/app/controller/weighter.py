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

    def __init__(self):
        """
        Controller for weighting all submission components. Generates final
        feedback too.
        """
        super().__init__()

    def execute_first_stage(self):
        if self._next_stage_id is not None:
            return

        self.execute_stage(self.stages_ids[0])

    def select_stage(self, stage_id):
        """
        Select a stage always.
        """
        stage_info = self.stages[stage_id]
        self.view.show_stage(stage_id, stage_info.label)
        self.execute_stage(stage_id)

    def execute_stage(self, stage_id=None):
        """
        Execute a stage if it hasn't been executed yet and is ready for
        execution.
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

        output = stage.OutputWeighting(self.model, stage_id, instance.outcomes)
        self.set_stage_output(self.current_stage[0], output)

    #
    # def refresh_stage(self, stage_id):
    #     if stage_id not in self.stages_handlers:
    #         raise stage.StageIgnorableError('Stage has not yet executed.')
    #
    #     instance = self.stages_handlers[stage_id]
    #     instance.refresh()
    #     self.set_stage_output(stage_id, instance.output)
    #
    # def report(self, result, stage_id=None, stage_info=None):
    #     """Report a stage result to the UI"""
    #     if stage_id is None or stage_info is None:
    #         stage_id   = self.current_stage[0]
    #         stage_info = self.current_stage[1]
    #
    #     self.add_score(stage_id, 'reported', result.score)
    #
    #     if result.result == stage.StageResult.RESULT_PASS or \
    #             result.result == stage.StageResult.RESULT_PASS_NONFINAL:
    #         state = stage.StageInfo.STATE_COMPLETE
    #         self.view.set_stage_state(stage_id, state)
    #
    #         if result.output is not None:
    #             self.set_stage_output(stage_id, result.output)
    #         try:
    #             next_stage_id = self.get_next_stage_id(stage_id)
    #             next_stage    = self.stages[next_stage_id]
    #
    #             if next_stage.state == stage.StageInfo.STATE_INACTIVE:
    #                 self._next_stage_id = next_stage_id
    #
    #             if result.result == stage.StageResult.RESULT_PASS and \
    #                     self.progress_on_success:
    #                 self.execute_stage(next_stage_id)
    #         except KeyError:
    #             pass
    #
    #     elif result.result == stage.StageResult.RESULT_PARTIAL:
    #         state = stage.StageInfo.STATE_COMPLETE
    #         self.view.set_stage_state(stage_id, state)
    #         self.set_stage_output(stage_id, result.output)
    #
    #     else:
    #         state  = stage.StageInfo.STATE_FAILED
    #
    #         if stage_info.halt_on_error:
    #             for _, stage_ in self.stages.items():
    #                 stage_.set_state(stage.StageInfo.STATE_FAILED)
    #
    #         self.view.set_stage_state(self.current_stage[0], state)
    #         self.set_stage_output(self.current_stage[0], result.output)
    #
    #         self.view.show_alert(stage_info.label,
    #                              result.error,
    #                              stage_info.halt_on_error)
    #
    #     feedback_post = stage_info.feedback_post
    #     if feedback_post is not None and len(feedback_post.strip()) > 0:
    #         self.add_feedeback(stage_id, '__post', feedback_post)
    #
