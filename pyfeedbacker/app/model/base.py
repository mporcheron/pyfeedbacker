# -*- coding: utf-8 -*-

from collections import OrderedDict

import abc



class StagesData(OrderedDict):
    def __init__(self, data_type):
        """
        Base class for storing all the data for a stage in the model. Its
        expected that any specific data type will extended this class and
        provide the data container type through calling __init__ on super()
        """
        self._data_type = data_type

    def __getitem__(self, stage_id):
        stage_id = str(stage_id)
        try:
            return super().__getitem__(stage_id)
        except KeyError:
            super().__setitem__(stage_id, self._data_type(stage_id))
            return super().__getitem__(stage_id)

    def __contains__(self, stage_id):
        stage_id = str(stage_id)
        try:
            return super().__contains__(stage_id)
        except KeyError:
            return False

    list = property(lambda self:self.__list__(), doc="""
            Get a copy of the data as a list.
            """)

    def _get_as_list(self):
        items = []

        for value in self.values():
            items += value.list

        return items

    def __list__(self):
        return self._get_as_list()

    dict = property(lambda self:self.__dict__(), doc="""
            Get a copy of the data as a dictionary.
            """)

    def __dict__(self):
        items = {}

        for key, value in self.items():
            items[key] = value.dict

        return items



class Data(OrderedDict):
    def __init__(self, stage_id, init_value):
        """
        Base data class for the model. Its expected that any specific data
        type will extended this class and provide an initial/default value
        through calling __init__ on super()
        """
        self.stage_id   = stage_id
        self.init_value = init_value

    def __getitem__(self, data_id):
        data_id = str(data_id)
        try:
            return super().__getitem__(data_id)
        except KeyError:
            super().__setitem__(data_id, self.init_value)
            return super().__getitem__(data_id)

    def __setitem__(self, data_id, value):
        data_id = str(data_id)
        return super().__setitem__(data_id, value)

    def __contains__(self, data_id):
        data_id = str(data_id)
        try:
            return super().__contains__(data_id)
        except KeyError:
            return False

    list = property(lambda self:self.__list__(), doc="""
            Return the data as a list.
            """)

    @abc.abstractmethod
    def __list__(self):
        pass

    dict = property(lambda self:self.__dict__(), doc="""
            Return the feedbacks as a dict.
            """)

    @abc.abstractmethod
    def __dict__(self):
        pass