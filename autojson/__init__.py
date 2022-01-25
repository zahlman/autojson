from collections import UserList, UserString
from collections.abc import Iterable


__version__ = '0.1.0'


class Node:
    def __init__(self, parent, key, *args, **kwargs):
        if parent is not None and not isinstance(parent, Node):
            raise TypeError('parent must be a Node or None')
        super().__init__(*args, **kwargs)
        self._parent = parent
        self._key = key


class Proxy(Node):
    def __getitem__(self, key):
        return Proxy(self, key)


    def _replace_me(self, where):
        if not isinstance(where, int):
            raise NotImplementedError
        my_replacement = self._parent._replace_me(self._key)
        my_replacement[where] = Array([None]*(where+1), my_replacement, where)
        return my_replacement[where]


    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._parent._replace_me(self._key)[key] = value
        else:
            raise NotImplementedError


    def __repr__(self):
        return 'undefined'


class Terminal(Node):
    def __getitem__(self, key):
        return Proxy(self._parent, self._key)[key]


    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._parent._replace_me(self._key)[key] = value
        else:
            raise NotImplementedError


class Null(Terminal):
    def __repr__(self):
        return 'null' 


class Array(Node, UserList):
    def __init__(self, items, parent=None, key=None):
        super().__init__(parent, key, [create(x, self, i) for i, x in enumerate(items)])


    def _replace_me(self, where):
        self[where] = []
        return self[where]


    def __setitem__(self, key, value):
        if isinstance(key, int):
            count = len(self.data)
            self.data += [Null(self, i) for i in range(count, key+1)]
            self.data[key] = create(value, self, key)
        else:
            raise NotImplementedError


    # Ugly workaround so the wrapper appears for __repr__ only
    # and only at the top level. Need to clone in Object.
    def __str__(self):
        return UserList.__repr__(self)


    def __repr__(self):
        is_root = self._parent is None
        return f'autojson.create({self})' if is_root else str(self)


class String(Terminal, UserString):
    def __new__(cls, text, parent=None, key=None):
        if parent is None:
            return str(text)
        return super().__new__(cls)


    def __init__(self, text, parent=None, key=None):
        assert parent is not None
        assert isinstance(text, str)
        super().__init__(parent, key, text)


def create(data, parent=None, key=None):
    if data is None or isinstance(data, Null):
        return Null(parent, key)
    if isinstance(data, str):
        return String(data, parent, key)
    if isinstance(data, Iterable):
        return Array(data, parent, key)
    raise TypeError(f"can't make JSON from {data} of type {type(data)}")
