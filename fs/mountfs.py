from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import errors
from .base import FS
from .memoryfs import MemoryFS
from .mode import check_writable
from .path import abspath
from .path import forcedir
from .path import normpath
from .mode import validate_open_mode
from .mode import validate_openbin_mode


class MountError(Exception):
    """Thrown when mounts conflict."""


class MountFS(FS):
    """
    A virtual filesystem that maps directories on to other file-systems.

    :param auto_close: If True, the child filesystems will be closed
        when the ``MountFS`` is closed.
    :type auto_close: bool

    """

    _meta = {
        "virtual": True,
        "read_only": False,
        'unicode_paths': True,
        "case_insensitive": False,
        "invalid_path_chars": "\0",
    }

    def __init__(self, auto_close=True):
        super(MountFS, self).__init__()
        self.auto_close = auto_close
        self.default_fs = MemoryFS()
        self.mounts = []

    def __repr__(self):
        return "MountFS(auto_close={!r})".format(self.auto_close)

    def __str__(self):
        return "<mountfs>"

    def _delegate(self, path):
        """
        Get a tuple of (fs, path) for a mounted filesystem, or (None,
        None) if no filesystem is mounted on the given path.

        """
        _path = forcedir(abspath(normpath(path)))
        is_mounted = _path.startswith

        for mount_path, fs in self.mounts:
            if is_mounted(mount_path):
                return fs, _path[len(mount_path):].rstrip('/')

        return self.default_fs, path

    def mount(self, path, fs):
        """
        Mounts a host FS object on a given path.

        :param path: A path within the MountFS.
        :type path: str
        :param fs: A filesystem object to mount.
        :type fs: :class:`fsbase.FS`

        """
        if fs is self:
            raise ValueError('Unable to mount self')
        _path = forcedir(abspath(normpath(path)))

        for mount_path, _ in self.mounts:
            if _path.startswith(mount_path):
                raise MountError(
                    "mount point overlaps existing mount"
                )

        self.mounts.append((_path, fs))
        self.default_fs.makedirs(_path, recreate=True)

    def close(self):
        # Explicitly closes children if requested
        if self.auto_close:
            for _path, fs in self.mounts:
                fs.close()
            del self.mounts[:]
        self.default_fs.close()
        super(MountFS, self).close()

    def desc(self, path):
        if not self.exists(path):
            raise errors.ResourceNotFound(path)
        fs, delegate_path = self._delegate(path)
        return "{path} on {fs}".format(fs=fs, path=delegate_path)

    def getinfo(self, path, *namespaces):
        self._check()
        fs, _path = self._delegate(path)
        return fs.getinfo(_path, *namespaces)

    def listdir(self, path):
        self._check()
        fs, delegate_path = self._delegate(path)
        return fs.listdir(delegate_path)

    def makedir(self, path, permissions=None, recreate=False):
        self._check()
        fs, _path = self._delegate(path)
        return fs.makedir(
            _path, permissions=permissions, recreate=recreate)

    def openbin(self, path, mode='r', buffering=-1, **kwargs):
        validate_openbin_mode(mode)
        self._check()
        fs, _path = self._delegate(path)
        return fs.openbin(_path, mode=mode, buffering=-1, **kwargs)

    def remove(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.remove(_path)

    def removedir(self, path):
        self._check()
        path = normpath(path)
        if path in ('', '/'):
            raise errors.RemoveRootError(path)
        fs, _path = self._delegate(path)
        return fs.removedir(_path)

    def getbytes(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.getbytes(_path)

    def gettext(self, path, encoding=None, errors=None, newline=None):
        self._check()
        fs, _path = self._delegate(path)
        return fs.gettext(
            _path,
            encoding=encoding,
            errors=errors,
            newline=newline
        )

    def getsize(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.getsize(path)

    def getsyspath(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.getsyspath(path)

    def gettype(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.gettype(_path)

    def geturl(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.geturl(path)

    def hasurl(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.hasurl(_path)

    def isdir(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.isdir(_path)

    def isfile(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.isfile(_path)

    def scandir(self, path, namespaces=None):
        self._check()
        fs, _path = self._delegate(path)
        return fs.scandir(_path, namespaces=namespaces)

    def setinfo(self, path, info):
        self._check()
        fs, _path = self._delegate(path)
        return fs.setinfo(path, info)

    def validatepath(self, path):
        self._check()
        fs, _path = self._delegate(path)
        return fs.validatepath(_path)

    def open(self,
             path,
             mode='r',
             buffering=-1,
             encoding=None,
             errors=None,
             newline=None,
             **options):
        validate_open_mode(mode)
        self._check()
        fs, _path = self._delegate(path)
        return fs.open(
            _path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            **options
        )

    def setbytes(self, path, contents):
        self._check()
        fs, _path = self._delegate(path)
        return fs.setbytes(path, contents)

    def settext(self,
                path,
                contents,
                encoding='utf-8',
                errors=None,
                newline=None):
        fs, _path = self._delegate(path)
        return fs.settext(
            _path,
            contents,
            encoding=encoding,
            errors=errors,
            newline=newline
        )