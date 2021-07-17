# -*- coding: utf-8 -*-

from app.controller import scorer, marker
from app.model import fs as model
from app.view import urwid as view



def start_scorer(submission):
    c = scorer.Controller(submission)
    m = model.FileSystemModel()
    v = view.UrwidView(c, m)
    c.set_model(m).set_view(v).start()



def start_marker():
    c = marker.Controller()
    m = model.FileSystemModel()
    v = view.UrwidView(c, m)
    c.set_model(m).set_view(v).start()