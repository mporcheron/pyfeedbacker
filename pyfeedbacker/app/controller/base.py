# -*- coding: utf-8 -*-

from pyfeedbacker.app import config, stage

import abc



class BaseController:
    def __init__(self):
        """Default/base controller for all non-specific interfaces."""
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
        """Set the model that'll store information about a submission
        and then store scores/marks and feedback.

        Arguments:
        model -- Root model.
        """
        self.model     = model
        return self

    def set_view(self, view):
        """Set the view that will handle the entire interface for the
        application.

        Arguments:
        view -- UI handler.
        """
        self.view = view
        return self

    def start(self):
        """Start the application by loading stages and then the view, if it exists."""
        self._load_stages()

        if hasattr(self, 'view'):
            self.view.run()


    def _load_stages(self):
        """Load all stages from the configuration file."""
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

    def get_next_stage_id(self, stage_id):
        """Retrieve the stage identifier of the stage after the current one.

        Arguments:
        stage_id -- A valid stage identifier

        Returns:
        None if there is no following stage

        Raises:
        ValueError if stage_id is not valid
        """
        pos = self.stages_ids.index(stage_id)
        if pos+1 < len(self.stages_ids):
            next_stage_id = self.stages_ids[pos+1]
            return next_stage_id

        return None

    def set_stage_output(self, stage_id, output):
        """Set the output for a particular stage. Passes through to the view.
        
        Arguments:
        stage_id -- Unique textual identifier for the stage.
        output -- An output instance that extends `OutputBase`
        """
        self.view.set_stage_output(stage_id, output)

    def save_and_close(self):
        """Save the model to permanent storage and close the application."""
        self.model.save()
        
        if hasattr(self, 'view'):
           self.view.quit()

    @abc.abstractmethod
    def execute_stage(self, stage_id = None):
        """Execute a stage if it hasn't been executed yet.
        
        Keyword arguments:
        stage_id -- Stage to execute, or the next valid stage if None is 
            provided
        """
        pass

    @abc.abstractmethod
    def refresh_stage(self, stage_id):
        """Refresh a stage's output.
        
        Arguments:
        stage_id -- Stage to request to provide an updated output.
            provided
        """
        pass

    @abc.abstractmethod
    def report(self, result, stage_id = None, stage_info = None):
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
        pass