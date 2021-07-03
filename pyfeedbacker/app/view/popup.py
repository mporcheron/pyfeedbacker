# -*- coding: utf-8 -*-

from . import widgets as uw

from math import lcm

import urwid



class PopupDialog:
    DIALOG_CANCEL = 0
    DIALOG_QUIT   = 1

    def __init__(self, title, text):
        """
        Create a pop-up dialog to be shown floating over the UI.
        """
        self.title   = title
        self.text    = text
        self.buttons = []
        self.window  = None

    def add_buttons(self, buttons):
        """
        Based on https://github.com/urwid/urwid/blob/master/examples/dialog.py

        Modified to fit customisable actions.
        """
        l = []
        widths = []

        for name, _ in buttons:
            widths.append(len(name))
        width = max(widths)

        for name, action in buttons:
            padding = (' ' * int((width - len(name)) / 2))
            
            b = uw.SimpleButton(padding + name + padding, self._on_button_press)
            b.action = action
            b = urwid.AttrWrap(b, 'selectable', 'focus')
            l.append(b)

        buttons = urwid.GridFlow(l, width + 6, 3, 1, 'center')
        self.buttons = [urwid.Pile([urwid.Divider(), buttons], focus_item = 1)]

    def _on_button_press(self, button):
        """
        Callback when a button is pressed in the popup dialog.
        """
        if isinstance(button.action, int):
            if button.action == PopupDialog.DIALOG_CANCEL:
                self.loop.widget = self.window
            elif button.action == PopupDialog.DIALOG_QUIT:
                raise urwid.ExitMainLoop()
        else:
            self.loop.widget = self.window
            if button.action is not None:
                button.action(button._init_label)

    def show(self, loop, window):
        """
        Show the popup over the main frame.
        """
        self.loop   = loop
        self.window = window

        w = urwid.Pile([urwid.Divider(),
                        urwid.Text(('popup', self.text), 'center')] + \
                        self.buttons + [urwid.Divider()])
        w = urwid.LineBox(w, self.title)

        self.loop.widget =  urwid.Overlay(w,
                                          window,
                                          'center',
                                          ('relative', 60),
                                          'middle',
                                          'pack')
        self.loop.draw_screen()