from pathlib import Path
from typing import Dict, Iterator, List, Union
import json
import safer

# JSON is the type used by JSON, TOML, or Yaml
JSON = Union[Dict, List, None, bool, float, int, str]
JSON_Lines = Iterator[JSON]
FileData = Union[JSON, JSON_Lines]
FilePath = Union[Path, str]
JSON_LINE_SUFFIXES = '.jl', '.jsonl', '.jsonline'
# _NONE = object()


def read(path: FilePath) -> FileData:
    p = Path(path)

    if p.suffix == '.json':
        with p.open() as fp:
            return json.load(fp)

    if p.suffix == '.toml':
        try:
            import tomllib as toml
        except ImportError:
            toml = _toml()
        return toml.loads(p.read_text())

    if p.suffix == '.yaml':
        return _yaml().safe_load(p.read_text())

    if p.suffix in JSON_LINE_SUFFIXES:
        return _read_jl(p)

    raise ValueError(f'Cannot understand file {path}')


def write(data: FileData, path: FilePath, **kwargs: Dict) -> None:
    p = Path(path)

    if p.suffix == '.json':
        with safer.open(p, 'w') as fp:
            json.dump(data, fp)

    elif p.suffix == '.toml':
        p.write_text(_toml().dumps(data))

    if p.suffix == '.yaml':
        return _yaml().safe_load(p.read_text())

    if p.suffix in JSON_LINE_SUFFIXES:
        return _read_jl(p)

    raise ValueError(f'Cannot understand file {path}')


def _toml():
    try:
        import tomlkit
        return tomlkit
    except ImportError:
        raise ImportError('Install `tomlkit` to handle .toml files')


def _yaml()
    try:
        import pyyaml
        return pyyaml
    except ImportError:
        raise ImportError('Install `pyyaml` to handle .yaml files')


def _read_jl(path):
    with path.open() as fp:
        for line in fp:
            yield json.loads(line)
