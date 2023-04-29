from pathlib import Path
from typing import Dict, Iterator, List, Union
import json
import safer

__all__ = 'read', 'write', 'SUFFIX_TO_CLASS'

# JSON is the type used by JSON, TOML, or Yaml
JSON = Union[Dict, List, None, bool, float, int, str]
JSON_Lines = Iterator[JSON]
FileData = Union[JSON, JSON_Lines]
FilePath = Union[Path, str]


def read(path: FilePath) -> FileData:
    p = Path(path)
    return _get_class(p).read(p)


def write(data: FileData, path: FilePath, **kwargs: Dict) -> None:
    p = Path(path)
    return _get_class(p).write(data, p, **kwargs)


def _get_class(p):
    try:
        return SUFFIX_TO_CLASS[p.suffix]
    except KeyError:
        raise ValueError('Do not understand file {p}')


class _Json:
    @staticmethod
    def read(p):
        with p.open() as fp:
            return json.load(fp)

    @staticmethod
    def write(data, p):
        with safer.open(p, 'w') as fp:
            json.dump(data, fp)


class _Yaml:
    @staticmethod
    def read(p):
        with p.open() as fp:
            return _yaml().safe_load(fp)

    @staticmethod
    def write(data, p, **kwargs):
        with safer.open(p, 'w') as fp:
            _yaml().safe_dump(data, fp, **kwargs)


def _yaml():
    try:
        import pyyaml
        return pyyaml
    except ImportError:
        raise ImportError('Install `pyyaml` to handle .yaml files')


class _Toml:
    @staticmethod
    def read(p):
        try:
            import tomllib as toml
        except ImportError:
            toml = _toml()
        return toml.loads(p.read_text())

    @staticmethod
    def write(data, p, **kwargs):
        p.write_text(_toml().dumps(data, **kwargs))


def _toml():
    try:
        import tomlkit
        return tomlkit
    except ImportError:
        raise ImportError('Install `tomlkit` to handle .toml files')


class _JsonLines:
    @staticmethod
    def read(p):
        with p.open() as fp:
            for line in fp:
                yield json.loads(line)

    @staticmethod
    def write(data, p, *, use_safer=False, **kwargs):
        if kwargs.get('indent') is not None:
            raise ValueError('indent= not allowed for JSON Lines')

        _open = safer.open if use_safer else open
        with _open(p, 'w') as fp:
            for d in data:
                print(json.dumps(d), file=fp)


SUFFIX_TO_CLASS = {
    '.jl': _JsonLines,
    '.jsonl': _JsonLines,
    '.jsonline': _JsonLines,
    '.yaml': _Yaml,
    '.yml': _Yaml,
    '.json': _Json,
    '.toml': _Toml,
}
