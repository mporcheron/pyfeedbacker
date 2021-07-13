# -*- coding: utf-8 -*-

from .. import config, stage
from ..controller import scorer

import urwid
import statistics



class FooterWidget(urwid.WidgetWrap):

    def __init__(self, controller, model, window):
        """
        A full-width footer bar displaying statistics about the submissions.
        """
        self.controller = controller
        self.model      = model
        self.window     = window

        header_text = config.ini['app']['name']

        self._show_marks = False
        if isinstance(controller, scorer.Controller):
            self._show_marks = \
                config.ini['assessment'].getboolean('scores_are_marks', False)
            header_text += f' ({controller.submission})'
        
        header_text_widget = urwid.Text((header_text), align='left')
        header_text_len = len(header_text)

        self._show = 'score' if isinstance(controller, scorer.Controller) \
                     else 'mark'

        # widgets for values
        self._w_mean    = urwid.Text('-')
        self._w_mean_nz = urwid.Text('-')
        self._w_median  = urwid.Text('-')

        self._w_low     = urwid.Text('-')
        self._w_high    = urwid.Text('-')
        self._w_iqr     = urwid.Text('-')

        # add statistics information
        contents  = [urwid.Text(f'Mean f{self._show}'),
                     self._w_mean]
        contents += [urwid.Text(f'Mean {self._show} (no zeroes)'),
                     self._w_mean_nz]
        contents += [urwid.Text(f'Median {self._show}'),
                     self._w_median]
        contents += [urwid.Text(f'Lowest {self._show}'),
                     self._w_low]
        contents += [urwid.Text(f'Highest {self._show}'),
                     self._w_high]
        contents += [urwid.Text(f'IQR'),
                     self._w_iqr]

        col1labels = urwid.Pile([urwid.Text(f'Mean {self._show}'),
                                 urwid.Text(f'Mean {self._show} (no zeroes)'),
                                 urwid.Text(f'Median {self._show}')])
        col1values = urwid.Pile([self._w_mean, self._w_mean_nz, self._w_median])

        col2labels = urwid.Pile([urwid.Text(f'Lowest {self._show}'),
                                 urwid.Text(f'Highest {self._show}'),
                                 urwid.Text(f'IQR')])
        col2values = urwid.Pile([self._w_low, self._w_high, self._w_iqr])

        
        stats_panel = urwid.Columns([col1labels, col1values,
                                     col2labels, col2values], 1)
        stats_panel = urwid.Padding(stats_panel, left = 1, right = 1)


        self._widget = urwid.AttrMap(stats_panel, 'footer')
        super().__init__(self._widget)


    def set_statistics(self, stats):
        """
        Update the statistics displayed. Pass in a Statistics class (below)
        """
        self._w_mean.set_text(stats.mean)
        self._w_mean_nz.set_text(stats.mean_nz)
        self._w_median.set_text(stats.median)
        self._w_low.set_text(stats.low)
        self._w_high.set_text(stats.high)
        self._w_iqr.set_text(stats.iqr)



    class Statistics:
        def __init__(self):
            self.reset()

        def reset(self):
            self.values = []

        def add_value(self, val):
            self.values.append(val)

        mean = property(lambda self:str(statistics.fmean(self.values)), doc="""
                Read-only mean value for the data.
                """)

        mean_nz = property(lambda self:'{:.2f}'.format(statistics.fmean(
                                [i for i in self.values if i != 0])),
                           doc="""
                Read-only mean value for the data, excluding zeroes.
                """)

        median = property(lambda self:'{:.2f}'.format(
                                statistics.median(self.values)),
                          doc="""
                Read-only median value for the data.
                """)

        low = property(lambda self:'{:.2f}'.format(min(self.values)), doc="""
                Read-only lowest value for the data.
                """)

        high = property(lambda self:'{:.2f}'.format(max(self.values)), doc="""
                Read-only highest value for the data.
                """)

        iqr = property(lambda self:self._calc_iqr(), doc="""
                Read-only inter-quartile range for the data.
                """)

        def _calc_iqr(self):
            q = statistics.quantiles(self.values, n=4, method='inclusive')
            iqr = q[2] - q[1]
            return f'{iqr:.2f}'
