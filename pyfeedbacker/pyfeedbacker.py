# -*- coding: utf-8 -*-

from app.controller import marker, weighter
from app.model import fs as model
from app.view import urwid as view



def start_marker(submission):
    c = marker.Controller(submission)
    m = model.FileSystemModel()
    v = view.UrwidView(c, m)
    c.set_model(m).set_view(v).start()



def start_weighter():
    c = weighter.Controller()
    m = model.FileSystemModel()
    v = view.UrwidView(c, m)
    c.set_model(m).set_view(v).start()

    raise NotImplementedError('Weighting application is not implemented yet')