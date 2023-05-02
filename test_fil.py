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

COMPRESS_SUFFIXES = [''] + list(fil.SUFFIX_TO_COMPRESSION)
PAIRS = itertools.product(DATA, fil.SUFFIX_TO_CLASS, COMPRESS_SUFFIXES)


@pytest.mark.parametrize('data, suffix, compress', list(PAIRS))
@tdir
def test_fil(data, suffix, compress):
    file_name = 'data' + suffix + compress
    is_jl = 'j' in suffix and 'l' in suffix

    expect_error = (
        (suffix == '.txt' and not isinstance(data, str))
        or (suffix == '.toml' and not isinstance(data, dict))
        or (is_jl and not isinstance(data, list))
    )

    if expect_error:
        with pytest.raises(TypeError) as e:
            fil.write(data, file_name)
        msg = e.value.args[0]
        if is_jl:
            expected = 'JSON Line data must be iterable and not dict or str'
            assert msg == expected
        else:
            assert 'files only accept' in msg
    else:
        fil.write(data, file_name)
        round_trip = fil.read(file_name)
        if is_jl:
            round_trip = list(round_trip)

        assert data == round_trip
