# -*- coding: utf-8 -*-

from app import marker, weighter
from app.model import fs


def start_marker(submission):
    c = marker.Controller(submission)
    m = fs.FileSystemModel()
    v = marker.UrwidView(c, m)
    c.set_model(m).set_view(v).start()



def start_weighter():
    raise NotImplementedError('Weighting application is not implemented yet')