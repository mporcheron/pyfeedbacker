# -*- coding: utf-8 -*-

from pyfeedbacker.app.controller import base

import sys



class Controller(base.BaseController):
    def __init__(self, submission):
        """Controller for deleting the outcomes for a submission."""
        super().__init__()

        self.submission      = submission

    def start(self):
        deleted = False

        try:
            del self.model.feedbacks[self.submission]
            deleted = True
        except KeyError:
            sys.stderr.write(
                f'No feedback for submission "{self.submission}".\n')
        try:
            del self.model.outcomes[self.submission]
            deleted = True
        except KeyError:
            sys.stderr.write(
                f'No outcomes for submission "{self.submission}".\n')

        if deleted:
            self.model.save()
            print(f'Submission {self.submission} deleted.')
