# -*- coding: utf-8 -*-

from .. import config, stage
from ..controller import scorer

import urwid
import math
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

        self._show_scores = False
        if isinstance(controller, scorer.Controller):
            self._showing_scores = True

        self._show_text = 'score' if isinstance(controller, scorer.Controller) \
                           else 'mark'

        # widgets for values
        self._w_mean    = urwid.Text('-')
        self._w_mean_nz = urwid.Text('-')
        self._w_median  = urwid.Text('-')

        self._w_low     = urwid.Text('-')
        self._w_high    = urwid.Text('-')
        self._w_iqr     = urwid.Text('-')

        # add statistics information
        contents  = [urwid.Text(f'Mean f{self._show_text}'),
                     self._w_mean]
        contents += [urwid.Text(f'Mean {self._show_text} (no zeroes)'),
                     self._w_mean_nz]
        contents += [urwid.Text(f'Median {self._show_text}'),
                     self._w_median]
        contents += [urwid.Text(f'Lowest {self._show_text}'),
                     self._w_low]
        contents += [urwid.Text(f'Highest {self._show_text}'),
                     self._w_high]
        contents += [urwid.Text(f'IQR'),
                     self._w_iqr]

        col1labels = urwid.Pile([urwid.Text(f'Mean {self._show_text}'),
                                 urwid.Text(f'Mean {self._show_text} '
                                            f'(no zeroes)'),
                                 urwid.Text(f'Median {self._show_text}')])
        col1values = urwid.Pile([self._w_mean, self._w_mean_nz, self._w_median])

        col2labels = urwid.Pile([urwid.Text(f'Lowest {self._show_text}'),
                                 urwid.Text(f'Highest {self._show_text}'),
                                 urwid.Text(f'IQR')])
        col2values = urwid.Pile([self._w_low, self._w_high, self._w_iqr])

        
        stats_panel = urwid.Columns([col1labels, col1values,
                                     col2labels, col2values], 1)
        stats_panel = urwid.Filler(stats_panel, top = 1, min_height = 5)
        stats_panel = urwid.BoxAdapter(stats_panel, height = 5)
        stats_panel = urwid.Padding(stats_panel, left = 1, right = 1)

        self._graph = urwid.BarGraph(
            attlist=['footer', 'graph bg 1', 'graph bg 2'],
            hatt={
                (1, 0): 'graph bg 1',
                (2, 0): 'graph bg 2'
            },
            satt={
                (1, 0): 'graph bg 1 smooth',
                (2, 0): 'graph bg 2 smooth'
            }
        )

        graph = urwid.Padding(self._graph, left = 1, right = 1)
        graph = urwid.BoxAdapter(graph, height=5)

        no_cols_w = urwid.Columns([urwid.Text('-', align = 'center')])
        self._axis = urwid.WidgetWrap(no_cols_w)
        
        graph_panel = urwid.Pile([graph, self._axis])

        self._widget = urwid.AttrMap(
            urwid.Columns([stats_panel, graph_panel]),
            'footer')
        super().__init__(self._widget)


    def set_statistics(self, stats):
        """
        Update the statistics displayed. Pass in a Statistics class (below)
        """
        if len(stats.values) == 0:
            return

        self._w_mean.set_text(stats.mean)
        self._w_mean_nz.set_text(stats.mean_nz)
        self._w_median.set_text(stats.median)
        self._w_low.set_text(stats.low)
        self._w_high.set_text(stats.high)
        self._w_iqr.set_text(stats.iqr)

        showing = FooterWidget.Statistics.GRAPH_SCORES if self._show_scores \
                  else FooterWidget.Statistics.GRAPH_MARKS
        (axis, data, max_value) = stats.graph_data(showing)

        axis_w = [urwid.Text(str(x), align='center') for x in axis]
        self._axis._w = urwid.Columns(axis_w)

        data = [([y] if x%2==0 else [0,y]) for x, y in enumerate(data)]
        self._graph.set_data(data, max_value)


    class Statistics:
        GRAPH_SCORES, GRAPH_MARKS = range(0,2)

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

        def graph_data(self, showing):
            if showing == FooterWidget.Statistics.GRAPH_SCORES:
                min_value = config.ini['assessment'].getfloat('score_min', None)
                max_value = config.ini['assessment'].getfloat('score_max', None)
            elif showing == FooterWidget.Statistics.GRAPH_MARKS:
                min_value = config.ini['assessment'].getfloat('score_min', None)
                max_value = config.ini['assessment'].getfloat('score_max', None)
            else:
                raise AttributeError('The attribute `showing` must be '
                                     'GRAPH_SCORES or GRAPH_MARKS')

            if min_value is None:
                min_value = self.low
            if max_value is None:
                max_value = self.high

            num_cols = config.ini['app'].getint('graph_columns', 10)
            if num_cols < 1:
                num_cols = 10
            step = (max_value - min_value) / num_cols

            counts = [0] * num_cols
            for i in self.values:
                # if a key doesn't exist that means it is the maximum value
                try:
                    counts[math.floor(i / step)] += 1            
                except:
                    counts[-1] += 1


            axis = list(range(math.floor(min_value),
                              math.ceil(max_value),
                              int(step)))

            return (axis, counts, max(counts))