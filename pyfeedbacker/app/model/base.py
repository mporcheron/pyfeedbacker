# -*- coding: utf-8 -*-

from collections import OrderedDict

import abc



class AbstractModelContainer(OrderedDict):
    def __init__(self, child_data_type = None, parent_data_id = None):
        """Base class for storing data by ID. Its expected that any specific 
        data type will extended this class and provide the data container type through calling `__init__` on `super()`.

        This is essentially an `collections.OrderedDict`.

        Keyword arguments:
        child_data_type -- A data type that will be stored inside this 
            container. New data will be initialised to an instance of this type.
        parent_data_id -- ID of the parent data container, if it exists.
        """
        self._child_data_type = child_data_type
        self._parent_data_id  = parent_data_id

    def __getitem__(self, data_id):
        """Retrieve an item using the square bracket syntax. If a particular 
        `data_id` doesn't exist, then one will be created with an initialised
        value passed into `__init__`.

        Arguments:
        data_id -- Identifier for a piece of data, will be converted to a 
            string if it isn't already a string.
        """
        data_id = str(data_id)
        try:
            return super().__getitem__(data_id)
        except KeyError:
            if self._child_data_type is None:
                new_obj = None
            elif issubclass(self._child_data_type, AbstractModelContainer):
                new_obj = self._child_data_type(parent_data_id = data_id)
            else:
                new_obj = self._child_data_type()
    
            self.__setitem__(data_id, new_obj)
            return new_obj

    def __setitem__(self, data_id, value):
        """Set an item using the square bracket syntax.

        Arguments:
        data_id -- Identifier for a piece of data, will be converted to a 
            string if it isn't already a string.
        value -- The value to store in the model.
        """
        data_id = str(data_id)

        # If value is inserted somewhere else, delete the existing one
        try:
            existing_index = list(self.values()).index(value)
            existing_key = list(self.keys())[existing_index]
            del self[existing_key]
        except:
            pass

        # If the data_id is not correct inside value, change it
        try:
            child_parent_id = value._parent_data_id
            if data_id != child_parent_id:
                value._parent_data_id = data_id
        except:
            pass

        return super().__setitem__(data_id, value)

    def __contains__(self, data_id):
        """Determine if a particular  `data_id` exists.

        Arguments:
        data_id -- Identifier for a piece of data, will be converted to a 
            string if it isn't already a string.
        """
        data_id = str(data_id)
        return super().__contains__(data_id)

    dict = property(lambda self:self.__dict__(), doc="""
            Retrieve a copy of the data as a new dictionary.
            """)

    @abc.abstractmethod
    def __dict__(self):
        """Retrieve a copy of the data as a new dictionary."""
        return dict(self.items())

    def __repr__(self):
        ret  = f'{self.__class__.__name__}('
        ret += str(list(self))
        ret += ')'

        return ret



class DataByStage(AbstractModelContainer):
    def __init__(self, child_data_type, parent_data_id):
        """Create a container for storing data for each stage.
        
        Arguments:
        child_data_type -- A data type that will be stored inside this 
            container. New data will be initialised to an instance of this type.
        parent_data_id -- The identifier of the key in the parent container,
            which in this case is the submission identifier.
        """
        super().__init__(child_data_type = child_data_type,
                         parent_data_id  = parent_data_id)

    submission = property(lambda self:self._parent_data_id, doc="""
            Retrieve the submission identifier
            """)

    def __dict__(self):
        """Retrieve a copy of the data as a new dictionary."""
        items = {}

        for key, value in self.items():
            items[key] = value.dict

        return items



class Data(AbstractModelContainer):
    pass