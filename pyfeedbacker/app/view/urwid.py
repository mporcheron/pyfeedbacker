# -*- coding: utf-8 -*-

from ..view import window



class UrwidView:
    def __init__(self, controller, model):
        """
        Public API for the pyfeedbacker UI, which is all self-contained
        in a separate package (app.view) using Urwid
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
