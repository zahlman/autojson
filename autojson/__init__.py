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
        # the empty array will get expanded as the recursion bubbles up.
        my_replacement[where] = Array([], my_replacement, where)
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
    # represents None.
    def __repr__(self):
        return 'null'


class Array(Node, UserList):
    def __init__(self, items, parent=None, key=None):
        # copy subtree and ensure list type for storage.
        data = [create(x, self, i) for i, x in enumerate(items)]
        super().__init__(parent, key, data)


    def __iter__(self):
        # Needed for copying instances.
        # Because of the auto-creation, the default implementation would
        # be an infinite loop. This happens because collections.abc.Sequence
        # implements a mixin `__iter__` with a while loop, rather than
        # counting elements ahead of time with `__len__` - even though
        # `Sequence` demands that `__len__` is available.
        yield from self.data


    def _replace_me(self, where):
        self[where] = []
        return self[where]


    def _ensure(self, amount):
        self.data += [None] * (amount + 1 - len(self.data))


    def __getitem__(self, key):
        if not isinstance(key, int):
            raise NotImplementedError # TODO: slices
        try:
            return _wrap(self.data[key], self, key)
        except IndexError:
            return Proxy(self, key)


    def __setitem__(self, key, value):
        if isinstance(key, int):
            count = len(self.data)
            self._ensure(key)
            self.data[key] = create(value, self, key) # copy subtree
        else:
            raise NotImplementedError


    def __str__(self):
        contents = ', '.join(
            'null' if x is None else repr(x)
            for x in self.data
        )
        return f'[{contents}]'


    def __repr__(self):
        is_root = self._parent is None
        return f'autojson.create({self})' if is_root else str(self)


class String(Terminal, UserString):
    pass


def _wrap(data, parent=None, key=None):
    if data is None:
        return Null(parent, key)
    if isinstance(data, str):
        return String(parent, key)
    return data


def create(data, parent=None, key=None):
    if isinstance(data, str) or data is None:
        return data
    if isinstance(data, Iterable):
        return Array(data, parent, key)
    raise TypeError(f"can't make JSON from {data} of type {type(data)}")
