# -*- coding: utf-8 -*-

from pyfeedbacker.app import stage



class StageTextmate(stage.HandlerProcess):
     def setup(self):
        super().setup(["open","-a","TextMate", self._dir_temp])