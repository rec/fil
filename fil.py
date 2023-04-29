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


class _Base:
    suffixes = ()
    use_safer = True
    module_names = ()

    def __init__(self):
        for m in self.module_names:
            try:
                self._module = __import__(m)
                return
            except ImportError:
                pass
        self._import_error()

    def _import_error(self):
        name = self.module_name
        sfx = ', '.join(self.suffixes)
        raise ImportError(f'Install module `{name}` is needed for {sfx} files')

    def read(self, p):
        with p.open() as fp:
            return self._read(fp)

    def write(self, data, p, *, **kwargs):
        use_safer = kwargs.pop('use_safer', None)
        if use_safer is None:
            use_safer = self.use_safer:
        fp = safer.open(p) if use_safer else open(p)
        with fp:
            self._write(data, fp, **kwargs)

    def _open(self, p, kwargs):
        use_safer = kwargs.pop('use_safer', None)
        if use_safer is None:
            use_safer = self.use_safer:
        return safer.open(p) if use_safer else open(p)

    @property
    def _read(self):
        return self._module.load

    @property
    def _write(self):
        return self._module.dump


class _Json(_Base):
    suffixes = '.json',
    module_names = 'json',


class _Toml(_Base):
    suffixes = '.toml',
    module_names = 'tomlkit',

    @property
    def _write(self):
        try:
            return super()._write
        except AttributeError:
            self._import_error()


class _Yaml(_Base):
    suffixes = '.yaml', '.yml'
    module_names = 'pyyaml',

    @property
    def _read(self):
        return self._module.safe_load

    @property
    def _write(self):
        return self._module.safe_dump


class _JsonLines:
    use_safer = False
    suffixes = '.jl', '.jsonl', '.jsonlines'

    def _read(self, p):
        for line in fp:
            yield json.loads(line)

    def _write(self, data, p, *, **kwargs):
        if kwargs.get('indent') is not None:
            raise ValueError('indent= not allowed for JSON Lines')

        for d in data:
            print(json.dumps(d), file=fp)


class _Json:
    @staticmethod
    def read(p):
        with p.open() as fp:
            return json.load(fp)

    @staticmethod
    def write(data, p, *, use_safer=True, **kwargs):
        with _open(p, use_safer) as fp:
            json.dump(data, fp, **kwargs)


class _Yaml:
    @staticmethod
    def read(p):
        with p.open() as fp:
            return _yaml().safe_load(fp)

    @staticmethod
    def write(data, p, *, use_safer=True, **kwargs):
        with _open(p, use_safer) as fp:
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
    def write(data, p, *, use_safer=True, **kwargs):
        with _open(p, use_safer) as fp:
            _toml().dump(data, fp, **kwargs)


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

        with _open(p, use_safer) as fp:
            for d in data:
                print(json.dumps(d), file=fp)


SUFFIX_TO_CLASS = {
    '.jl': _JsonLines,
    '.json': _Json,
    '.jsonl': _JsonLines,
    '.jsonline': _JsonLines,
    '.toml': _Toml,
    '.yaml': _Yaml,
    '.yml': _Yaml,
}
