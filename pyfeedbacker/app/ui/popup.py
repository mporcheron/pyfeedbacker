# -*- coding: utf-8 -*-

from .. import config as cfg
from . import widgets as uw

from math import lcm

import urwid


class PopupDialog:
    DIALOG_CANCEL = 0
    DIALOG_QUIT   = 1

    def __init__(self, title, text):
        """
        Create a pop-up dialog
        """
        self.title   = title
        self.text    = text
        self.buttons = []
        self.window  = None

    def add_buttons(self, buttons):
        """
        Based on https://github.com/urwid/urwid/blob/master/examples/dialog.py

        Modified to fit customisable actions
        """
        l = []
        widths = []

        for name, action in buttons:
            widths.append(len(name))

        width = lcm(*widths)

        for name, action in buttons:
            padded_name = (' ' * (int(((width - len(name))/2)))) + name
            b = uw.SimpleButton(padded_name, self.respond_to_button)
            b.action = action
            b = urwid.AttrWrap(b, 'selectable', 'focus')
            l.append(b)

        buttons = urwid.GridFlow(l, width + 6, 3, 1, 'center')
        self.buttons = [urwid.Pile([urwid.Divider(), buttons], focus_item = 1)]

    def respond_to_button(self, button):
        if isinstance(button.action, int):
            if button.action == PopupDialog.DIALOG_CANCEL:
                self.loop.widget = self.window
            elif button.action == PopupDialog.DIALOG_QUIT:
                raise urwid.ExitMainLoop()
        else:
            self.loop.widget = self.window
            button.action()

    def show(self, loop, window):
        self.loop   = loop
        self.window = window

        w = urwid.Pile([urwid.Text(('popup', self.text))] + self.buttons)
        w = urwid.LineBox(w, self.title)

        self.loop.widget =  urwid.Overlay(w,
                                          window,
                                          'center',
                                          ('relative', 60),
                                          'middle',
                                          'pack')
        self.loop.draw_screen()