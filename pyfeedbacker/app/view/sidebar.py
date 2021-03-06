# -*- coding: utf-8 -*-

from pyfeedbacker.app import stage
from pyfeedbacker.app.view import adapters as ua, urwid as uu, widgets as uw

import urwid
import math



class SidebarStagesWidget(urwid.WidgetWrap):
    SIDEBAR_WIDTH = 32

    def __init__(self, controller, model, view, window):
        """Create the sidebar of the UI for selecting stages."""
        self.controller = controller
        self.model      = model
        self.view       = view
        self.window     = window

        self._stages_buttons  = {}
        self._stages          = []
        self._stage_id_to_pos = {}
        self._active_pos      = None
        
        self._show_state = self.view.app == uu.UrwidView.APP_SCORER

        contents = [urwid.Divider(),
                    urwid.AttrMap(urwid.Text(u'Stage'),
                    'sidebar title'),
                    urwid.Divider()]

        w  = urwid.Pile(contents)
        w = urwid.Padding(w, left = 4, right = 4)
        self._listwalker = urwid.SimpleFocusListWalker([w])

        w = urwid.ListBox(self._listwalker)
        self._widget = urwid.AttrMap(w, 'sidebar')

        super().__init__(self._widget)

    def get_width(self):
        return SidebarStagesWidget.SIDEBAR_WIDTH

    def append_stage(self, stage_info):
        """
        Add a stage to the end of the sidebar, which the user can select
        as part of the marking process.
        """
        w = SidebarStagesWidget.StageButton(stage_info.label,
                                            self.get_width(),
                                            stage_info.state,
                                            self._on_select_stage,
                                            stage_info,
                                            self._show_state)
        self._stages_buttons[stage_info.stage_id] = w
        self._stages.append(stage_info)
        self._stage_id_to_pos[stage_info.stage_id] = len(self._stages)

        w = urwid.AttrMap(w, 'stage', 'stage focus')
        self._listwalker.append(w)

    def _on_select_stage(self, widget, stage):
        """Callback for when the user selects a stage in the sidebar"""
        self.controller.select_stage(stage.stage_id)

    def get_next_stage(self):
        """
        Retrieve the next stage in the sidebar after the current selected
        stage. Returns None if there is no next stage.
        """
        try:
            next_stage = self._stages[self._active_pos]
            return next_stage
        except IndexError:
            return None

    def set_stage_selected(self, stage_id):
        """
        Set which stage is to be highlighted as active. Throws an AttributeError
        if the stage_id is invalid.
        """
        try:
            w = self._listwalker[self._active_pos]
            w.set_attr_map({None: 'stage'})
        except:
            pass

        try:
            stage_pos = self._stage_id_to_pos[stage_id]
            self._active_pos = stage_pos

            w = self._listwalker[stage_pos]
            w.set_attr_map({None: 'stage active'})
        except KeyError:
            raise AttributeError(f'No stage matching stage id f{stage_id}')

    def set_stage_state(self, stage_id, state):
        """
        Set the state (inactive, active, failed, complete etc.) of a stage.
        """
        try:
            self._stages_buttons[stage_id].set_state(state)
        except KeyError:
            raise AttributeError(f'No stage matching stage id f{stage_id}')

        self.window.loop.draw_screen()

    class StageButton(uw.SimpleButton):
        button_left  = u' '
        button_right = u''

        def __init__(self,
                     label,
                     width,
                     state,
                     on_press   = None,
                     user_data  = None,
                     show_state = True):
            """Button for the user to select on the sidebar."""
            self._stage_label = label
            self._width       = width
            self._show_state  = show_state

            label = self.generate_label(state)
            super().__init__(label, on_press, user_data)

        def generate_label(self, state):
            """Label with the state icon shown on the far right."""
            text = self.get_state_icon(state) + ' ' + self._stage_label

            num_chars = len(text)
            num_lines = math.ceil(num_chars / self._width)

            if text.startswith('  Task 10'):
                zz = 1

            if num_lines > 1:
                line = 1
                pos = 0
                line_pos = 0
                while pos < num_chars:
                    ch = text[pos]
                    line_pos += 1

                    if line_pos >= self._width:
                        line_pos = 0
                        spaces = 1

                        while text[pos] != ' ':
                            pos -= 1
                            spaces += 1

                        text = text[:pos] + (' ' * spaces) + text[pos:] 
                        line_pos += 3
                        num_chars = len(text)
                        pos += spaces
                        line += 1

                    pos += 1

            return text

        def get_state_icon(self, state):
            """Retrieve the icon for the current state of the stage."""
            if self._show_state:
                if state == stage.StageInfo.STATE_INACTIVE:
                    return ' '
                elif state == stage.StageInfo.STATE_ACTIVE:
                    return '???'
                elif state == stage.StageInfo.STATE_COMPLETE:
                    return '???'
                elif state == stage.StageInfo.STATE_FAILED:
                    return '???'
                else:
                    return '!'
                    
            return ' '

        def set_state(self, state):
            """Change the state of the label (and update the button)."""
            super().set_label(self.generate_label(state))