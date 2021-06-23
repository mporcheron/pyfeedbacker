# -*- coding: utf-8 -*-

from .. import config as cfg
from .. import stage
from . import adapters as ua
from . import widgets as uw

import urwid


class SidebarWidget(urwid.WidgetWrap):
    SIDEBAR_WIDTH = 32
    
    def __init__(self, controller, model, window):
        """Create the sidebar of the UI for selecting stages."""
        self.controller = controller
        self.model      = model
        self.window     = window
        
        self._stages_buttons = {}
        self._stages         = []

        contents = [urwid.Divider(),
                    urwid.AttrWrap(urwid.Text(u'Stage'),
                    'sidebar title'),
                    urwid.Divider()]

        w  = urwid.Pile(contents)
        w = urwid.Padding(w, left = 4, right = 4)
        self._listwalker = urwid.SimpleFocusListWalker([w])

        w = urwid.ListBox(self._listwalker)
        self._widget = urwid.AttrWrap(w, 'sidebar')
        
        super(SidebarWidget, self).__init__(self._widget)

    def get_width(self):
        return SidebarWidget.SIDEBAR_WIDTH

    def append_stage(self, stage_info):
        """Add a stage to the end of the sidebar"""
        w = SidebarWidget.StageButton(stage_info.label,
                                      self.get_width(),
                                      stage_info.state,
                                      self._on_select_stage,
                                      stage_info)
        self._stages_buttons[stage_info.stage_id] = w
        self._stages.append(stage_info)

        w = urwid.AttrMap(w, 'stage', 'stage active')
        self._listwalker.append(w)
        
    def _on_select_stage(self, widget, stage):
        """Show the output of a given stage"""
        self.controller.select_stage(stage.stage_id)
   
    def get_next_stage(self):
        try:
            next_pos   = self._listwalker.focus + 1
            next_stage = self._stages[next_pos - 1]
            return next_stage
        except IndexError:
            return None
   
    def set_stage_selected(self, stage_id):
        for stage_pos, stage_info in enumerate(self._stages):
            if stage_info.stage_id == stage_id:
                self._widget.set_focus_path([stage_pos+1])
                return
        
        raise stage.StageError(f'No stage matching stage id f{stage_id}')
        #         # self.controller.select_stage(stage_info.stage_id)
        # next_pos   = self._listwalker.focus + 1
        # next_stage = self._stages[next_pos - 1]
        # return next_stage

    def set_stage_state(self, stage_id, state):
        """Set the state of a stage"""
        self._stages_buttons[stage_id].set_state(state)
        self.window.loop.draw_screen()

    class StageButton(uw.SimpleButton):
        button_left  = u'  > '
        button_right = u''

        def __init__(self,
                     label,
                     width,
                     state,
                     on_press  = None,
                     user_data = None):
            self._stage_label = label
            self._width       = width

            label = self.generate_label(state)
            super(SidebarWidget.StageButton, self).__init__(label,
                                                           on_press,
                                                           user_data)

        def generate_label(self, state):
            state_icon_padding, state_icon = self.get_state_icon(state)
            return self._stage_label + state_icon_padding + state_icon

        def get_state_icon(self, state):
            padding = ' ' * (self._width - 3 - len(self._stage_label) - 5   )
            if state == stage.StageInfo.STATE_INACTIVE:
                return (padding, '・')
            elif state == stage.StageInfo.STATE_ACTIVE:
                return (padding, '✽')
            elif state == stage.StageInfo.STATE_COMPLETE:
                return (padding, '✓')
            elif state == stage.StageInfo.STATE_FAILED:
                return (padding, '✗')
            else:
                return (padding, '!')

        def set_state(self, state):
            super(uw.SimpleButton, self).set_label(self.generate_label(state))