import itertools

import pytest
import tdir

try:
    import tomlkit

    TOMLKIT = bool(tomlkit)

except ImportError:
    TOMLKIT = False

import fil

DATA = (
    None,
    False,
    {},
    [],
    23,
    32.5,
    'five',
    {'hello': 'world'},
    {'a': {'very': {'deep': {'one': 'two'}}}},
    [{'a': 1, 'b': 2, 'c': 3}, {'a': 9, 'b': 7, 'c': 9}, {}],
    itertools,
)

PAIRS = itertools.product(fil.SUFFIX_TO_CLASS, DATA)


@pytest.mark.parametrize('suffix, data', list(PAIRS))
@tdir
def test_fil(suffix, data):
    file_name = 'data' + suffix
    is_jl = 'j' in suffix and 'l' in suffix

    if False and suffix == '.toml' and isinstance(data, dict):
        with open(file_name, 'wb') as fp:
            if 'hello' in data:
                fp.write(b'hello = "world"\n')
            else:
                fp.write(b'[a.very.deep]\none = "two"\n')
        round_trip = fil.read(file_name)
        assert round_trip == data

    expect_error = (
        (suffix == '.txt' and not isinstance(data, str))
        or (suffix == '.toml' and not (isinstance(data, dict) and TOMLKIT))
        or (is_jl and not isinstance(data, list))
        or (data is itertools)
    )

    if expect_error:
        with pytest.raises(Exception) as e:
            fil.write(data, file_name)

        msg = e.value.args[0]

        if is_jl:
            expected = 'JSON Line data must be iterable and not dict or str'
            assert msg == expected
        elif data is itertools:
            assert msg == 'cannot represent an object' or 'module' in msg
        else:
            assert (
                msg == 'Install module `tomlkit` to use .toml files'
                or 'files only accept' in msg
            )

    else:
        fil.write(data, file_name)
        round_trip = fil.read(file_name)
        if is_jl:
            round_trip = list(round_trip)

        assert data == round_trip


def test_default():
    assert fil.read('non-existent.json', 'none') == 'none'
