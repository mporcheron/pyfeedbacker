# -*- coding: utf-8 -*-

from .ui import window

from collections import OrderedDict


class UrwidView:
    def __init__(self, controller, model):
        """Public API for the pyfeedbacker UI, which is all self-contained 
        in a separate package (app.ui) using Urwid
        """
        self.controller = controller
        self.model      = model
        self.window     = window.WindowWidget(controller, model)

    def run(self):
        """Start the view"""
        self.window.run()

    def set_score(self, score):
        self.window.set_score(score)
        
    def append_stage(self, stage):
        # self.stages_ids.append(stage.stage_id)
        self.window.append_stage(stage)
        
    def append_stages(self, stages):
        for stage_id, stage in stages.items():
            self.append_stage(stage)
    
    def show_alert(self, title, text, halt_execution=False):
        self.window.show_alert(title, text, halt_execution)
    
    def show_stage(self, stage_id, label):
        self.window.show_stage(stage_id, label)
        
    def set_stage_state(self, stage_id, state):
        self.window.set_stage_state(stage_id, state)
        
    def set_stage_output(self, stage_id, output):
        self.window.set_stage_output(stage_id, output)
        
    def set_executable(self, stage_id):
        """
        Set that a stage has no blockers (i.e. earlier non-completed stages)
        and can be executed.
        """
        # self.window.set_progressable(stage_id)
    
    def quit(self):
        self.window.quit()




