# -*- coding: utf-8 -*-

import urwid



class SimpleButton(urwid.Button):
    """
    Custom Urwid button to hide cursor

    Based on https://stackoverflow.com/a/44682928
    """
    button_left  = u'< '
    button_right = u' >'

    def __init__(self, label, on_press=None, user_data=None):
        self._label = SimpleButton.ButtonLabel(u'')

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
        '''
        use Drunken Master's trick to move the cursor out of view
        '''
        def set_text(self, label):
            '''
            set_text is invoked by Button.set_label
            '''
            self.__super.set_text(label)
            self._cursor_position = len(label) + 1


class AutoWidthButton(SimpleButton):
    button_left  = u'< '
    button_right = u' >'

    def __init__(self,
                 label,
                 on_press  = None,
                 user_data = None):

        self._width = len(AutoWidthButton.button_left) + \
                      len(AutoWidthButton.button_right) + \
                      len(label)

        label = label
        super(AutoWidthButton, self).__init__(label,
                                              on_press,
                                              user_data)


class JumpablePile(urwid.Pile):

    def keypress(self, size, key):
        """
        A jumpable Pile allows you to press alt/option/meta + up/down arrow
        to jump up/down the pile to focus.

        Also loops at the top and bottom.
        """
        first_focus_position = None
        last_focus_position = None
        for wi, w in enumerate(self.contents):
            if w[0].selectable():
                first_focus_position = wi
                break

        for wi, w in enumerate(reversed(self.contents)):
            if w[0].selectable():
                last_focus_position = len(self.contents) - wi - 1
                break

        if (self.focus_position == first_focus_position and key == 'up') \
                or key == 'meta down':
            self.focus_position = last_focus_position
        elif (self.focus_position == last_focus_position and key == 'down') \
                or key == 'meta up':
            self.focus_position = first_focus_position
        else:
            return super(JumpablePile, self).keypress(size, key)


class JumpableColumns(urwid.Columns):

    def keypress(self, size, key):
        """
        A jumpable Columns allows you to press alt/option/meta + right/left 
        arrow to jump right/left accross the columns to focus.

        Also loops at the left and right.
        """
        first_focus_position = None
        last_focus_position = None
        for wi, w in enumerate(self.contents):
            if w[0].selectable():
                first_focus_position = wi
                break

        for wi, w in enumerate(reversed(self.contents)):
            if w[0].selectable():
                last_focus_position = len(self.contents) - wi - 1
                break

        if (self.focus_position == first_focus_position and key == 'left') \
                or key == 'meta f':
            self.focus_position = last_focus_position
        elif (self.focus_position == last_focus_position and key == 'right') \
                or key == 'meta b':
            self.focus_position = first_focus_position
        else:
            return super(JumpableColumns, self).keypress(size, key)


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
        if key == 'esc':
            self.escape_to()
        else:
            return super(EscableListBox, self).keypress(size, key)


class CentredRadioButton(urwid.RadioButton):
    
    def __init__(self, group, state="first True",
                 on_state_change=None, user_data=None):
        super(CentredRadioButton, self).__init__(group, '', state,
                                                 on_state_change, user_data)
                                                 
                                                 
    def set_state(self, state, do_callback=True):
        self.__super.set_state(state, do_callback)
        self._w = urwid.Columns( [
                    self._label,
                    ('fixed', self.reserve_columns, self.states[state] ),
                    self._label ] )
