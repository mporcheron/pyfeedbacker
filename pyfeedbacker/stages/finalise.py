# -*- coding: utf-8 -*-

from pyfeedbacker.app import config, stage

import os
import subprocess



class StageFinalise(stage.HandlerPython):
    def __init__(self, stage_id):
        """Does nothing.

        Arguments:
        stage_id -- The current stage in the process (we should know this as   
            this is the file for this stage, but this is just passed in for 
            clarity)
        """
 
        super().__init__(stage_id)
    def run(self):
        """Run a command using subprocess to open Textmate."""
        result = stage.StageResult(stage.StageResult.RESULT_PASS)
        result.set_output(self.output)
        return result