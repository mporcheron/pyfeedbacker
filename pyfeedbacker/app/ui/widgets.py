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