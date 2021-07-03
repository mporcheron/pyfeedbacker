# -*- coding: utf-8 -*-

from .. import config
from .. import marker
from .. import stage

import urwid



class HeaderWidget(urwid.WidgetWrap):

    def __init__(self, controller, model, window):
        """
        A full-width header bar for the application, displaying the configurable
        name of the application and if marks = scores, the current mark for
        the student if in marking mode.
        """
        self.controller = controller
        self.model      = model
        self.window     = window

        header_text = config.ini['app']['name']

        self._show_marks = False
        if isinstance(controller, marker.Controller):
            self._show_marks = \
                config.ini['assessment'].getboolean('scores_are_marks', False)
            header_text += f' ({controller.submission})'
        
        header_text_widget = urwid.Text((header_text), align='left')
        header_text_len = len(header_text)

        # add header content
        header_content = [urwid.Divider()]

        if self._show_marks:
            self.marks_str  = '-'
            (marks_text, marks_len) = self.get_marks_str()
            self.w_marks = urwid.Text(marks_text, align='right')

            header_content.append(
                urwid.Columns([
                    urwid.Padding(header_text_widget,
                                  left      = 4,
                                  right     = 4,
                                  min_width = header_text_len),
                    urwid.Padding(self.w_marks,
                                  left      = 4,
                                  right     = 4,
                                  min_width = marks_len)], 3))
        else:
            header_content.append(
                urwid.Padding(header_text_widget,
                              left      = 4,
                              right     = 4,
                              min_width = header_text_len))

        header_content.append(urwid.Divider())

        self._widget = urwid.AttrWrap(urwid.Pile(header_content), 'header')

        super(HeaderWidget, self).__init__(self._widget)

    def set_score(self, score):
        """
        Update the score displayed in the header widget.
        """
        if not self._show_marks:
            return

        self.marks_str = score
        self.update()

    def get_marks_str(self):
        """
        Get the string that shows the current and maximum number of marks. Only
        returns a string if the configuration value scores_are_marks is True.
        """
        if not self._show_marks:
            return ('', 0)

        marks_text = (str(self.marks_str) +
                     '/' +
                      config.ini['assessment']['score_max'])
        marks_len  = len(marks_text)
        return (marks_text, marks_len)

    def update(self):
        """
        Force the header to be updated
        """
        (marks_text, _) = self.get_marks_str()
        self.w_marks.set_text(marks_text)