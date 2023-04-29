"""
🏺 `fil`: Read or write JSON, TOML, Yaml and JSON Lines files 🏺

## Example 1: read a file

    # Reading a JSON Line file returns an interator:
    for record in fil.read('file.jsonl'):
        ...

## Example 2: write a file

    fil.write(d3, 'file.json')
    fil.write(d2, 'file.toml')
    fil.write(d1, 'file.yaml')

    # Write an iterator to a JSON Line file
    dicts = ({'key': i} for i in range(10))
    fil.write(dicts, 'file.jsonl')

"""

from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union
import json
import safer

__all__ = 'read', 'write', 'SUFFIX_TO_CLASS'

# JSON is the type used by JSON, TOML, or Yaml
JSON = Union[Dict, List, None, bool, float, int, str]
JSON_Lines = Iterator[JSON]
FileData = Union[JSON, JSON_Lines]
FilePath = Union[Path, str]


def read(path: FilePath) -> FileData:
    """
    Returns:
       JSON, or an iterator of JSON records, if the file is JSON Lines

    Args:
      path: the string or path to the file to read
    """
    p = Path(path)
    return _get_class(p).read(p)


def write(
    data: FileData,
    path: FilePath,
    *,
    use_safer: Optional[bool] = None,
    **kwargs: Dict,
) -> None:
    """
    Args:
      data: JSON, or an iterator of JSON records, if the file is JSON Lines

      path: the string or path to the file to read

      use_safer: whether to use the safer module to avoid writing incomplete
        files.  The default, `None` means use the default for that sort of file
        which is True for all files except JSON Line files, where the
        expectation is that a partial file be written if there is some error
        during the process.

      kwargs: named arguments passed to the underlying reader or writer
    """
    p = Path(path)
    return _get_class(p).write(data, p, use_safer=use_safer, **kwargs)


def _get_class(p):
    try:
        return SUFFIX_TO_CLASS[p.suffix]
    except KeyError:
        raise ValueError('Do not understand file {p}')


class _Json:
    module_names = 'json',
    suffixes = '.json',
    use_safer = True

    def __init__(self):
        for m in self.module_names:
            try:
                self._module = __import__(m)
                return
            except ImportError:
                pass
        self._import_error()

    def read(self, p):
        with open(p) as fp:
            return self._read(fp)

    def write(self, data, p, use_safer=None, **kwargs):
        if use_safer or use_safer is None and self.use_safer:
            fp = safer.open(p, 'w')
        else:
            fp = open(p, 'w')

        with fp:
            self._write(data, fp, **kwargs)

    def _import_error(self):
        name = self.module_names[0]
        if name == 'yaml':
            name = 'pyyaml'

        sfx = ', '.join(self.suffixes)
        raise ImportError(f'Install module `{name}` is needed for {sfx} files')

    @property
    def _read(self):
        return self._module.load

    @property
    def _write(self):
        try:
            return self._module.dump
        except AttributeError:
            self._import_error()


class _Toml(_Json):
    suffixes = '.toml',
    module_names = 'tomlkit',


class _Yaml(_Json):
    suffixes = '.yaml', '.yml'
    module_names = 'yaml',

    @property
    def _read(self):
        return self._module.safe_load

    @property
    def _write(self):
        return self._module.safe_dump


class _JsonLines(_Json):
    use_safer = False
    suffixes = '.jl', '.jsonl', '.jsonlines'

    def read(self, p):
        with open(p) as fp:
            for line in fp:
                yield json.loads(line)

    def _write(self, data, fp, **kwargs):
        if kwargs.get('indent') is not None:
            raise ValueError('indent= not allowed for JSON Lines')

        for d in data:
            print(json.dumps(d), file=fp)


CLASSES = _Json(), _JsonLines(), _Toml(), _Yaml()
SUFFIX_TO_CLASS = {s: c for c in CLASSES for s in c.suffixes}
