# -*- coding: utf-8 -*-

from pyfeedbacker.app.controller import scorer, marker
from pyfeedbacker.app.model import fs as model
from pyfeedbacker.app.view import urwid as view

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