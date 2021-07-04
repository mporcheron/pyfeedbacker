# -*- coding: utf-8 -*-

from .. import config, stage

from collections import OrderedDict

import abc
import importlib
import threading



class BaseController:

    def __init__(self):
        """
        Default/base controller for all non-specific interfaces.
        """
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

    def get_next_stage_id(self, stage_id):
        pos = self.stages_ids.index(stage_id)
        if pos+1 < len(self.stages_ids):
            next_stage_id = self.stages_ids[pos+1]
            return next_stage_id

        return None

    def set_stage_output(self, stage_id, output):
        self.view.set_stage_output(stage_id, output)

    def save_and_close(self):
        self.model.save()
        self.view.quit()

    @abc.abstractmethod
    def execute_stage(self, stage_id=None):
        pass

    @abc.abstractmethod
    def refresh_stage(self, stage_id):
        pass

    @abc.abstractmethod
    def report(self, result, stage_id=None, stage_info=None):
        pass