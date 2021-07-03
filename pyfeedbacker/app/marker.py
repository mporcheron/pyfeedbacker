# -*- coding: utf-8 -*-

from . import config
from . import stage
from .ui import window

from collections import OrderedDict

import importlib
import os
import sys
import threading



class Controller:

    def __init__(self, submission):
        """
        Controller for marking a submission by a student and generating scores
        and feedback, separated by 'stages'.
        """
        self.submission      = submission
        
        # containers for the marking stages
        self.stages_ids      = []
        self.stages          = {}
        self.stages_handlers = {}

        self._next_stage_id = None
        self.current_stage = None

        # configuration information
        self.debug = config.ini['app'].getboolean('debug', False)

        default_ini = config.ini['assessment']
        self.progress_on_success = default_ini.getboolean(
            'progress_on_success', True)
        self.halt_on_error       = default_ini.getboolean(
            'halt_on_error', False)

    def set_model(self, model):
        """
        Set the model that'll store information about a submission
        and then store scores/marks and feedback.
        """
        self.model     = model
        self.scores    = model['scores'][self.submission]
        self.feedbacks = model['feedbacks'][self.submission]
        return self

    def set_view(self, view):
        """
        Set the view that will handle the entire interface for the
        application.
        """
        self.view = view
        return self

    def start(self):
        self._load_stages()
        self.view.run()

    def add_score(self, stage_id, score_id, value):
        self.scores[stage_id][score_id] = value
        self.view.set_score(self.scores.sum)

    def add_feedback(self, stage_id, feedback_id, value):
        self.feedbacks[stage_id][feedback_id] = value

    def _load_stages(self):
        """
        Load all stages from the configuration file.
        """
        stages = config.ini['assessment']['stages'].split(',')
        for stage_id in stages:
            stage_id  = stage_id.strip()
            s_ini = config.ini['stage_' + stage_id]

            stage_info = stage.StageInfo(
                controller    = self,
                stage_id      = stage_id,
                label         = s_ini['label'],
                handler       = s_ini['handler'],
                score_min     = s_ini.get('score_min', None),
                score_max     = s_ini.get('score_max', None),
                feedback_pre  = s_ini.get('feedback_pre',None),
                feedback_post = s_ini.get('feedback_post', None),
                halt_on_error = s_ini.getboolean(
                 'halt_on_error', self.halt_on_error))

            self.stages_ids.append(stage_id)
            self.stages[stage_id] = stage_info

        self.view.append_stages(self.stages)

    def select_stage(self, stage_id):
        """
        Select a stage and:
        1) if it hasn't been executed, and
        2) everything before it has been executed
        then it will be executed
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

    def execute_first_stage(self):
        if self._next_stage_id is None:
            self._next_stage_id = self.stages_ids[0]
            self.execute_stage(self._next_stage_id)

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
            instance = stage_info.handler()

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

            if self.progress_on_success:
                self.progress()

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
            self.report(result)

    def refresh_stage(self, stage_id):
        if stage_id not in self.stages_handlers:
            raise stage.StageIgnorableError('Stage has not yet executed.')

        instance = self.stages_handlers[stage_id]
        instance.refresh()
        self.set_stage_output(stage_id, instance.output)

    def get_next_stage_id(self, stage_id):
        pos = self.stages_ids.index(stage_id)
        if pos+1 < len(self.stages_ids):
            next_stage_id = self.stages_ids[pos+1]
            return next_stage_id

        return None

    def report(self, result, stage_id=None, stage_info=None):
        """Report a stage result to the UI"""
        if stage_id is None or stage_info is None:
            stage_id   = self.current_stage[0]
            stage_info = self.current_stage[1]

        self.add_score(stage_id, 'reported', result.score)

        if result.result == stage.StageResult.RESULT_PASS:
            state = stage.StageInfo.STATE_COMPLETE
            self.view.set_stage_state(stage_id, state)

            if result.output is not None:
                self.set_stage_output(stage_id, result.output)

            if self.progress_on_success:
                self.progress()
            else:
                try:
                    next_stage_id = self.get_next_stage_id(stage_id)
                    next_stage    = self.stages[next_stage_id]

                    if next_stage.state == stage.StageInfo.STATE_INACTIVE:
                        self._next_stage_id = next_stage_id
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

    def set_stage_output(self, stage_id, output):
        self.view.set_stage_output(stage_id, output)

    def save_and_close(self):
        self.model.save()
        self.view.quit()



class UrwidView:
    def __init__(self, controller, model):
        """
        Public API for the pyfeedbacker UI, which is all self-contained
        in a separate package (app.ui) using Urwid
        """
        self.controller = controller
        self.model      = model
        self.window     = window.Window(controller,
                                        model,
                                        window.Window.SIDEBAR_STAGES)

    def run(self):
        self.window.run()

    def append_stage(self, stage):
        self.window.append_stage(stage)

    def append_stages(self, stages):
        for stage_id, stage in stages.items():
            self.append_stage(stage)

    def show_alert(self, title, text, halt_execution=False):
        self.window.show_alert(title, text, halt_execution)

    def show_stage(self, stage_id, label):
        self.window.show_stage(stage_id, label)

    def set_score(self, score):
        self.window.set_score(score)

    def set_stage_state(self, stage_id, state):
        self.window.set_stage_state(stage_id, state)

    def set_stage_output(self, stage_id, output):
        self.window.set_stage_output(stage_id, output)

    def quit(self):
        self.window.quit()



