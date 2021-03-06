# -*- coding: utf-8 -*-

from pyfeedbacker.app.view import window as uw

from ..controller import scorer, marker



class UrwidView:
    APP_SCORER, APP_MARKER = range(0,2)
    ALERT_HALT, ALERT_OK, ALERT_YESNO = range(0,3)

    def __init__(self, controller, model):
        """
        Public API for the pyfeedbacker UI, which is all self-contained
        in a separate package (app.view) using Urwid
        """
        self.controller = controller

        self.app        = UrwidView.APP_SCORER
        if isinstance(controller, scorer.Controller):
            pass
        elif isinstance(controller, marker.Controller):
            self.app    = UrwidView.APP_MARKER
        else:
            raise AttributeError('Unknown app controller')

        self.model      = model
        self.window     = uw.Window(controller,
                                    model,
                                    self,
                                    uw.Window.SIDEBAR_STAGES)

    def run(self):
        self.window.run()

    def append_stage(self, stage):
        self.window.append_stage(stage)

    def append_stages(self, stages):
        for stage_id, stage in stages.items():
            self.append_stage(stage)

    def show_alert(self, title, text,
            alert_type=ALERT_OK, callback=None, buttons=None):
        if alert_type == UrwidView.ALERT_HALT:
            self.window.show_alert(title, text, True)
        elif alert_type == UrwidView.ALERT_OK:
            self.window.show_alert(title, text, False)
        elif alert_type == UrwidView.ALERT_YESNO:
            self.window.show_custom_alert(title, text, callback, buttons)

    def show_stage(self, stage_id, label):
        self.window.show_stage(stage_id, label)

    def set_score(self, score):
        self.window.set_score(score)

    def update_marks(self):
        self.window.update_marks()

    def set_stage_state(self, stage_id, state):
        self.window.set_stage_state(stage_id, state)

    def set_stage_output(self, stage_id, output):
        self.window.set_stage_output(stage_id, output)

    def quit(self):
        self.window.quit()
