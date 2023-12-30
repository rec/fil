import itertools

import pytest
import tdir
import yaml

import fil

DATA = (
    None,
    False,
    {},
    [],
    23,
    32.5,
    "five",
    {"hello": "world"},
    {"a": {"very": {"deep": {"one": "two"}}}},
    [{"a": 1, "b": 2, "c": 3}, {"a": 9, "b": 7, "c": 9}, {}],
    itertools,
)

PAIRS = itertools.product(fil.SUFFIX_TO_CLASS, DATA)


@pytest.mark.parametrize("suffix, data", list(PAIRS))
@tdir
def test_fil(suffix, data):
    file_name = "data" + suffix
    is_jl = "j" in suffix and "l" in suffix

    expect_error = (
        (suffix == ".txt" and not isinstance(data, str))
        or (suffix == ".toml" and not isinstance(data, dict))
        or (is_jl and not isinstance(data, list))
        or (data is itertools)
    )

    if expect_error:
        with pytest.raises((TypeError, yaml.YAMLError)) as e:
            fil.write(data, file_name)
        msg = e.value.args[0]
        if is_jl:
            expected = "JSON Line data must be iterable and not dict or str"
            assert msg == expected
        elif data is itertools:
            if isinstance(e.value, yaml.YAMLError):
                assert msg == "cannot represent an object"
            else:
                assert "module" in msg
        else:
            assert "files only accept" in msg
    else:
        fil.write(data, file_name)
        round_trip = fil.read(file_name)
        if is_jl:
            round_trip = list(round_trip)

        assert data == round_trip


def test_default():
    assert fil.read("non-existent.json", "none") == "none"
