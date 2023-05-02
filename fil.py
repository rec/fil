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

from functools import cached_property
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union
import bz2
import gzip
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
    cls, opener = _get_class_opener(p)
    return cls.read(p, opener)


def write(
    data: FileData,
    path: FilePath,
    *,
    use_safer: Optional[bool] = None,
    **kwargs: Dict,
) -> None:
    """Args:

    data: JSON, or an iterator of JSON records, if the file is JSON Lines

    path: the string or path to the file to read

    use_safer: whether to use the safer module to avoid writing incomplete
      files. The default, `None` means to use `safer` on all files *except*
      for JSON Line files, where you want each line to be immediately written
      as it appears, and a partial file saved if there is a crash

    kwargs: named arguments passed to the underlying writer
    """
    p = Path(path)
    cls, opener = _get_class_opener(p)
    return cls.write(data, p, opener, use_safer=use_safer, **kwargs)


class _Json:
    module_names = 'json',
    suffixes = '.json',
    use_safer = True

    def read(self, p, opener):
        with opener(p) as fp:
            return self._read(fp)

    def write(self, data, p, opener, *, use_safer=None, **kwargs):
        self._check_data(data)

        if use_safer is None:
            use_safer = self.use_safer

        with safer.open(p, 'w', enabled=use_safer, opener=opener) as fp:
            self._write(data, fp, **kwargs)

    def _check_data(self, data):
        pass

    def _import_error(self):
        name = self.module_names[0]
        name = 'pyyaml' if name == 'yaml' else name

        sfx = ', '.join(self.suffixes)
        raise ImportError(f'Install module `{name}` to use {sfx} files')

    @cached_property
    def _module(self):
        for m in self.module_names:
            try:
                return __import__(m)
            except ImportError:
                pass
        self._import_error()

    @cached_property
    def _read(self):
        return self._module.load

    @cached_property
    def _write(self):
        try:
            return self._module.dump
        except AttributeError:
            # This happens because tomlkit has dump/dumps, but tomllib does not
            self._import_error()


class _Txt(_Json):
    suffixes = '.txt',
    use_safer = False

    def _check_data(self, d):
        if not isinstance(d, str):
            raise TypeError('.txt files only accept strings, not {type(data)}')

    def _read(self, p):
        return p.read()

    def _write(self, data, fp, **kwargs):
        fp.write(data)


class _Toml(_Json):
    suffixes = '.toml',
    module_names = 'tomlkit', 'tomllib'

    def _check_data(self, data):
        if not isinstance(data, dict):
            raise TypeError(f'TOML files only accept dicts, not {type(data)}')


class _Yaml(_Json):
    suffixes = '.yaml', '.yml'
    module_names = 'yaml',

    @cached_property
    def _read(self):
        return self._module.safe_load

    @cached_property
    def _write(self):
        return self._module.safe_dump


class _JsonLines(_Json):
    use_safer = False
    suffixes = '.jl', '.jsonl', '.jsonlines'

    def read(self, p, opener=None):
        with open(p) as fp:
            for line in fp:
                yield json.loads(line)

    def _write(self, data, fp, **kwargs):
        if kwargs.get('indent') is not None:
            raise ValueError('indent= not allowed for JSON Lines')

        for d in data:
            print(json.dumps(d), file=fp)

    def _check_data(self, d):
        if not isinstance(d, (dict, str)):
            try:
                return iter(d)
            except TypeError:
                pass
        raise TypeError('JSON Line data must be iterable and not dict or str')


CLASSES = _Json(), _JsonLines(), _Toml(), _Txt(), _Yaml()
SUFFIX_TO_CLASS = {s: c for c in CLASSES for s in c.suffixes}


class _TextAdaptor:
    def __init__(self, fp):
        self._fp = fp

    def __getattr__(self, k):
        return getattr(self._fp, k)

    def read(self, i=None) -> str:
        return self._fp.read(i).decode()

    def write(self, s):
        return self._fp.write(s.encode())

    def __iter__(self):
        return (i.decode() for i in self._fp)

    def __enter__(self):
        return self._fp.__enter__()

    def __exit__(self, *a):
        return self._fp.__exit__(*a)


class _Opener:
    def __init__(self, opener):
        self.opener = opener

    def __call__(self, filename, mode='r'):
        fp = self.opener.open(filename, mode + 'b')
        return _TextAdaptor(fp)


SUFFIX_TO_OPENER = {
    '.bz': _Opener(bz2),
    '.gz': _Opener(gzip),
    '.gzip': _Opener(gzip),
}


def _get_class_opener(p):
    opener = SUFFIX_TO_OPENER.get(p.suffix, open)
    if opener is not open:
        p = p.with_suffix('')

    try:
        cls = SUFFIX_TO_CLASS[p.suffix]
    except KeyError:
        raise ValueError('Do not understand file {p}')
    return cls, opener
