# -*- coding: utf-8 -*-

import urwid



class SimpleButton(urwid.Button):
    """
    Custom Urwid button without a visible cursor,

    Based on https://stackoverflow.com/a/44682928
    """
    button_left  = u'< '
    button_right = u' >'

    def __init__(self, label, on_press=None, user_data=None):
        self._init_label = label.strip()
        self._label = SimpleButton.ButtonLabel('')

        cols = urwid.Columns([
            ('fixed', len(self.button_left), urwid.Text(self.button_left)),
            self._label,
            ('fixed', len(self.button_right), urwid.Text(self.button_right))],
            dividechars=1)

        super(urwid.Button, self).__init__(cols)

        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)

    class ButtonLabel(urwid.SelectableIcon):
        """
        Use Drunken Master's trick to move the cursor out of view to hide it.
        """
        def set_text(self, label):
            """
            set_text is invoked by Button.set_label; we move the cursor position
            out of view and cascade to the urwid.Button set_text() function
            """
            self.__super.set_text(label)
            self._cursor_position = len(label) + 1



class AutoWidthButton(SimpleButton):
    button_left  = u'< '
    button_right = u' >'

    def __init__(self,
                 label,
                 on_press  = None,
                 user_data = None):
        """
        Create a button that responds to the width of the content as opposed to
        the size of the container.
        """
        self._width = len(AutoWidthButton.button_left) + \
                      len(AutoWidthButton.button_right) + \
                      len(label)

        label = label
        super().__init__(label, on_press, user_data)



class TabbleColumns(urwid.Columns):

    def __init__(self, widget_list, dividechars=0, focus_column=None,
            min_width=1, box_columns=None):
        super().__init__(widget_list, dividechars, focus_column,
            min_width, box_columns)

        self._command_map['tab']       = 'cursor right'
        self._command_map['shift tab'] = 'cursor left'

    def keypress(self, size, key):
        super().keypress(size, key)



class EscableListBox(urwid.ListBox):

    def __init__(self, body, escape_to):
        """
        A ListBox that when someone presses escape, it can shift the focus to
        another widget.

        To do this, pass the body in and the function that should be called
        on escape
        """
        self.escape_to = escape_to
        super(EscableListBox, self).__init__(body)

    def keypress(self, size, key):
        """
        If escape is pressed, the escape_to callback passed to __init__()
        is called, otherwise cascade to the ListBox keypress handler.
        """
        if key == 'esc':
            self.escape_to()
        else:
            return super().keypress(size, key)



class CentredRadioButton(urwid.RadioButton):

    def __init__(self,
                 group,
                 state           = "first True",
                 on_state_change = None,
                 user_data       = None):
        """
        A radio button that has no label and centres the checkbox in the
        centre.
        """
        super().__init__(group, '', state, on_state_change, user_data)

    def set_state(self, state, do_callback=True):
        """
        Cascade to the RadioButton (and CheckBox) state setting functions
        and then go and replace the widget ourselves with two empty labels
        either side of the checkbox.
        """
        super().set_state(state, do_callback)
        self._w = urwid.Columns( [
                    self._label,
                    ('fixed', self.reserve_columns, self.states[state] ),
                    self._label ] )
