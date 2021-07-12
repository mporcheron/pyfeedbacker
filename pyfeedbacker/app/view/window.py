# -*- coding: utf-8 -*-

from .. import config, stage
from . import adapters as ua
from . import header as uh
from . import footer as uf
from . import sidebar as us
from . import popup as up
from . import urwid as uu
from . import widgets as uw

from math import lcm

import urwid
import signal



class Window:
    SIDEBAR_STAGES, SIDEBAR_STATS = range(0,2)

    def __init__(self, controller, model, view, sidebar=SIDEBAR_STAGES):
        """
        The main application UI.
        """
        self.controller = controller
        self.model      = model
        self.view       = view

        self.palette = [
            ('title',          '', '', '', 'bold,#ff0', ''),
            ('selectable',     '', '', '', 'black',     'g58'),
            ('focus',          '', '', '', 'black',     '#ff0'),
            ('highlighted',    '', '', '', 'black',     '#ff0'),
            ('sidebar',        '', '', '', '#fff',      'g11'),
            ('sidebar title',  '', '', '', '#fff,bold', 'g11'),
            ('stage',          '', '', '', 'white',     'g11'),
            ('stage active',   '', '', '', '#fff',      'black'),
            ('stage focus',    '', '', '', '#000',       '#ff0'),
            ('table header',   '', '', '', '#fff,bold', 'g23'),
            ('table row',      '', '', '', '#fff,bold',  ''),
            ('faded',          '', '', '', 'g52',        ''),
            ('edit',           '', '', '', 'white',      'dark blue'),
            ('edit selected',  '', '', '', '#fff,bold',  'dark blue'),
            ('bg',             '', '', '', 'g7',         '#000')]

        self.header  = uh.HeaderWidget(controller, model, self)

        if self.view.app == uu.UrwidView.APP_SCORER:
            self.palette.append(
                ('header',         '', '', '', 'bold',      '#0af'))
            self.footer = None
        elif self.view.app == uu.UrwidView.APP_MARKER:
            self.palette.append(
                ('header',         '', '', '', 'bold',      '#d06'))
            self.footer = uf.FooterWidget(controller, model, self)



        if sidebar is Window.SIDEBAR_STAGES:
            self.sidebar = us.SidebarStagesWidget(controller, model, view, self)
        elif sidebar is Window.SIDEBAR_STATS:
            raise NotImplementedError('Statistics sidebar not implemented')
        else:
            raise NotImplementedError('Unknown sidebar')

        self._progression_possible = {}
        self._show_continue_button = []
        self._output_adapters = {}
        self._cache_fresh = []
        self._last_stage_id = None

    def _on_focus_sidebar(self):
        self.frame.set_focus_path(['body', 0])

    def run(self):
        """
        Generate the UI and then call back to execute the first stage
        """
        # main content
        contents = [('title', u"Loading...")]
        w = urwid.Text(contents)
        content = [
            urwid.Divider(),
            urwid.Padding(w, left=2, right=2, min_width=20)]
        self._main = urwid.SimpleFocusListWalker(content)

        # window layout
        body = urwid.Columns(
            [
                ('fixed', self.sidebar.get_width(), self.sidebar),
                uw.EscableListBox(self._main, self._on_focus_sidebar)
            ])

        l = [urwid.Divider(), body]
        w = urwid.ListBox(urwid.SimpleListWalker(l))

        self.frame = urwid.Frame(header = self.header,
                                 body   = body,
                                 footer = self.footer)
        self.popup_quit = None

        # start the main loop
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(2**24)
        screen.register_palette(self.palette)
        self.loop = urwid.MainLoop(self.frame,
                                   palette         = self.palette,
                                   unhandled_input = self._on_keypress,
                                   event_loop      = urwid.SelectEventLoop())
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.set_alarm_in(1, self._first_stage)

        # from https://www.programcreek.com/python/?code=zulip%2Fzulip-terminal%2Fzulip-terminal-master%2Fzulipterminal%2Fcore.py
        disabled_keys = {
            'susp': 'undefined',  # Disable ^Z - no suspending
            'stop': 'undefined',  # Disable ^S - enabling shortcut key use
            'quit': 'undefined',  # Disable ^\, ^4
        }

        try:
            signal.signal(signal.SIGINT, self._on_interrupt)
            old_signal_list = self.loop.screen.tty_signal_keys(**disabled_keys)
            self.loop.run()

        except Exception:
            self.loop.screen.tty_signal_keys(*old_signal_list)
            raise

        finally:
            self.loop.screen.tty_signal_keys(*old_signal_list)

    def _first_stage(self, loop, user_data):
        """
        Callback for the first stage to begin execution. Called when the UI
        is idle (i.e. ready).
        """
        return self.controller.execute_first_stage()

    def set_score(self, score):
        self.header.set_score(score)

    def _on_interrupt(self, sig, frame):
        if self.loop.widget != self.frame:
            return

        self.request_quit()

    def _on_next_stage(self, w=None):
        self.frame.set_focus_path(['body', 0])
        next_stage_info = self.sidebar.get_next_stage()

        # if the next stage is None, must be Save and Close time
        if next_stage_info is None:
            self.controller.save_and_close()
        else:
            self.controller.select_stage(next_stage_info.stage_id)

    def append_stage(self, stage_info):
        """
        Append a stage to the UI
        """
        self._last_stage_id = stage_info.stage_id
        self.sidebar.append_stage(stage_info)

        if stage_info.state == stage.StageInfo.STATE_FAILED:
            self.set_text(
                stage_info.stage_id,
                'This stage has errors that will prevent successful execution.')

    def show_stage(self, stage_id, label):
        """
        Switch the content shown to that of a different stage. If the stage
        hasn't begun execution yet, show a simple message.

        Note the stage output is cached inside the object
        """
        self.visible_stage_id    = stage_id
        self.visible_stage_label = label

        self.sidebar.set_stage_selected(stage_id)

        if len(self._main.positions()) > 1:
            for pos in range(1, self._main.positions()[1]+1):
                self._main.pop(pos)

        output = []

        # stage title
        title = urwid.Text(('title', self.visible_stage_label))
        output += [title, urwid.Divider()]

        # stage contents
        if self.visible_stage_id in self._output_adapters:
            adapter = self._output_adapters[self.visible_stage_id]
            output += adapter.output
        else:
            output += [urwid.Text('This stage has not generated an output.')]

        output += [urwid.Divider()]

        #  continue button
        if self.visible_stage_id in self._show_continue_button:
            continue_text = 'Continue'
            if self.visible_stage_id == self._last_stage_id:
                continue_text = 'Save and close'
            continue_text_len = len(continue_text) + 6

            b = uw.SimpleButton(continue_text,
                                on_press = self._on_next_stage)
            b = urwid.AttrWrap(b, 'selectable', 'focus')
            b = urwid.WidgetWrap(b)
            bs = urwid.GridFlow([b], continue_text_len, 3, 2, 'center')
            output += [bs]

        w = uw.JumpablePile(output)

        if self.visible_stage_id in self._output_adapters:
            adapter = self._output_adapters[self.visible_stage_id]
            if adapter.view_focus is not None:
                try:
                    w.set_focus_path([4] + adapter.view_focus)
                except IndexError:
                    pass

        w = urwid.Padding(w, left=2, right=2, min_width=20)

        self._main.append(w)

        # if self.visible_stage_id in self._show_continue_button:
        self._main.focus = 1
        self.frame.set_focus_path(['body', 1])

        self.refresh()

    def redraw_stage(self, stage_id):
        """
        Redraw the current stage (only acts if it is visible)
        """
        try:
            if self.visible_stage_id != stage_id:
                return

            self.show_stage(self.visible_stage_id, self.visible_stage_label)
        except AttributeError:
            pass

    def set_stage_state(self, stage_id, state):
        """
        Set the state of a stage
        """
        self.sidebar.set_stage_state(stage_id, state)

        if state == stage.StageInfo.STATE_FAILED:
            self.set_text(stage_id, 'This stage has failed. Execution halted.')
        elif state == stage.StageInfo.STATE_COMPLETE:
            self._show_continue_button.append(stage_id)

    def set_stage_output(self, stage_id, output):
        """
        Set the output for a particular stage. Invokes a UI adapter for the
        output based on its type (see ui.adapters.py) and rewdraws the stage.
        """
        sa = None
        if isinstance(output, stage.OutputNone) or output is None:
            sa = ua.AdapterNone(stage_id, self.controller, self.model, self)
        elif isinstance(output, stage.OutputText):
            sa = ua.AdapterText(stage_id, self.controller, self.model, self)
        elif isinstance(output, stage.OutputEditText):
            sa = ua.AdapterEditText(stage_id, self.controller, self.model, self)
        elif isinstance(output, stage.OutputForm):
            sa = ua.AdapterForm(stage_id, self.controller, self.model, self)
        elif isinstance(output, stage.OutputChecklist):
            sa = ua.AdapterChecklist(stage_id,
                                     self.controller,
                                     self.model,
                                     self)
        elif isinstance(output, stage.OutputMarker):
            sa = ua.AdapterMarker(stage_id,
                                  self.controller,
                                  self.model,
                                  self)
        else:
            raise AttributeError(f'No adapter for output for {stage_id}: ' +
                                 str(output))

        try:
            self._output_adapters[stage_id] = sa
            self._output_adapters[stage_id].set(output)
            self.redraw_stage(stage_id)
        except stage.StageError as se:
            self.show_alert('Error', str(se), True)

            if self.controller.debug:
                raise se

    def set_text(self, stage_id, text):
        """
        An override for output that'll output text only.
        """
        output = stage.OutputText(text)
        self.set_stage_output(stage_id, output)

    def set_progressable(self, stage_id):
        """
        Set that a stage has no blockers (i.e. earlier non-completed stages)
        and can be executed.
        """
        self._progression_possible[stage_id] = True

    def refresh(self):
        """
        Refresh/redraw the whole UI
        """
        if self.loop.screen._started:
            self.loop.draw_screen()

    def show_alert(self, title, text, halt_execution=False):
        w = up.PopupDialog(title, text)
        if halt_execution:
            w.add_buttons([(('Quit ' + config.ini['app']['name'],
                             up.PopupDialog.DIALOG_QUIT))])
        else:
            w.add_buttons([(('OK', up.PopupDialog.DIALOG_CANCEL))])

        w.show(self.loop, self.frame)

    def show_custom_alert(self, title, text, callback, options=['Yes','No']):
        w = up.PopupDialog(title, text)

        buttons = []
        for option in options:
            buttons.append((option, callback))

        w.add_buttons(buttons)
        w.show(self.loop, self.frame)

    def request_quit(self):
        """
        Show a popup asking if the user wants to quit pyfeedbacker
        """
        w = up.PopupDialog('Quit?',
                           'Are you sure you want to quit? ' +
                           'Any unsaved changes will be lost.')
        w.add_buttons([('Yes', up.PopupDialog.DIALOG_QUIT),
                       ('No',  up.PopupDialog.DIALOG_CANCEL)])
        w.show(self.loop, self.frame)

    def quit(self):
        raise urwid.ExitMainLoop()

    def _on_keypress(self, key):
        if self.loop.widget != self.frame:
            return

        if key == 'esc':
            if self.loop.widget == self.popup_quit:
                self.loop.widget = self.frame
            else:
                self.request_quit()
        elif key in ('q', 'Q'):
            self.request_quit()