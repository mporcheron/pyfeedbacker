# -*- coding: utf-8 -*-

from .. import config as cfg
from .. import stage

import urwid


class HeaderWidget(urwid.WidgetWrap):

    def __init__(self, controller, model, window):
        """Create the header bar of the UI."""
        self.controller = controller
        self.model      = model
        self.window     = window

        self.marks_str  = '-'

        header_text = cfg.ini['app']['name'] + f' ({model.submission})'
        header_text_widget = urwid.Text((header_text), align='left')
        header_text_len = len(header_text)

        (marks_text, marks_len) = self.get_marks_str()
        self.w_marks = urwid.Text(marks_text, align='right')

        header_content = [
            urwid.Divider(),
            urwid.Columns([
                urwid.Padding(header_text_widget,
                              left      = 4,
                              right     = 4,
                              min_width = header_text_len),
                urwid.Padding(self.w_marks,
                              left      = 4,
                              right     = 4,
                              min_width = marks_len)], 3),
            urwid.Divider()]

        self._widget = urwid.AttrWrap(urwid.Pile(header_content), 'header')

        super(HeaderWidget, self).__init__(self._widget)

    def set_score(self, score):
        """Update the score displayed in the header widget."""
        self.marks_str = score
        self.update()

    def get_marks_str(self):
        """
        Get the string that shows the current and maximum number of marks. Only
        returns a string if the configuration value scores_are_marks is True.
        """
        if not cfg.ini['assessment']['scores_are_marks']:
            return ('', 0)

        marks_text = (str(self.marks_str) +
                     '/' +
                      cfg.ini['assessment']['score_max'])
        marks_len  = len(marks_text)
        return (marks_text, marks_len)

    def update(self):
        (marks_text, _) = self.get_marks_str()
        self.w_marks.set_text(marks_text)