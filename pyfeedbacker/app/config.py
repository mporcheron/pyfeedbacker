# -*- coding: utf-8 -*-

import enum
import configparser
import copy



class ConfigWrapper:
    def __init__(self):
        self.clear()
        self.reset()

    def __getitem__(self, key):
        return self.ini[key]

    def __getattr__(self, attr):
        return self.ini.__getattribute__(attr)

    def clear(self):
        self.ini = configparser.ConfigParser()

    def reset(self):
        self.ini.read('config.ini')



ini = ConfigWrapper()