import fil
import itertools
import pytest
import tdir

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
)

PAIRS = itertools.product(fil.SUFFIX_TO_CLASS, DATA)


@pytest.mark.parametrize('suffix, data', list(PAIRS))
@tdir
def test_fil(suffix, data):
    if suffix == '.toml' and not isinstance(data, dict):
        return

    is_jl = 'j' in suffix and 'l' in suffix
    if is_jl and not isinstance(data, list):
        return

    file_name = 'data' + suffix
    fil.write(data, file_name)
    round_trip = fil.read(file_name)
    if is_jl:
        round_trip = list(round_trip)

    assert data == round_trip
