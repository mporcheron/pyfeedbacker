# -*- coding: utf-8 -*-

from app import marker, weighter


def start_marker(submission, dir_submissions, dir_temp, dir_output):
    c = marker.Controller()
    m = marker.Model(submission,
                     dir_submissions,
                     dir_temp,
                     dir_output)
    v = marker.UrwidView(c, m)
    c.set_model(m).set_view(v).start()



def start_weighter(dir_output):
    c = weighter.Controller()
    m = weighter.Model(dir_output)
    v = weighter.UrwidView(c, m)
    c.set_model(m).set_view(v).start()
