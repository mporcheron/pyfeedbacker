# -*- coding: utf-8 -*-

from app import marker, view


def start_marker(submission, dir_submissions, dir_temp,  dir_output):
    c = marker.Controller()
    m = marker.Model(submission,
                     dir_submissions,
                     dir_temp,
                     dir_output)
    v = view.UrwidView(c, m)
    c.set_model(m).set_view(v).start()
