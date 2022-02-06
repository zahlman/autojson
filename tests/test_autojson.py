from pytest import raises
from pytest import mark
parametrize, xfail = mark.parametrize, mark.xfail
from autojson import __version__, create


def test_version():
    assert __version__ == '0.1.0'


@parametrize('i,o', (([None], '[null]'), ([], '[]'), (['test'], "['test']")))
def test_simple(i, o):
    assert str(create(i)) == o


def test_proxying():
    x = create([])
    x[0][0][0][0][0] = 'test'
    assert str(x) == "[[[[['test']]]]]"
    y = create([])
    # Make sure it works with non-trivial auto-population too.
    y[1][1][1][1][1] = 'test'
    assert str(y) == "[null, [null, [null, [null, [null, 'test']]]]]"


def test_repr():
    # labelled only on the outermost layer
    assert repr(create(['a', [], None])) == "autojson.create(['a', [], null])"


def test_bad_root():
    assert create(None) is None 
    test = create('test')
    assert test == 'test' and type(test) is str


def test_populate():
    x = create([])
    x[3] = 'three'
    x[5] = 'five'
    assert str(x) == "[null, null, null, 'three', null, 'five']"


def test_get_no_mutate():
    x = create([])
    x[0][0][0][0]
    assert str(x) == "[]"
