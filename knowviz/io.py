"""Set of file-related operations
"""
import os as _os
import typing as _t
from hashlib import md5 as _md5

import pyparsing as _pp

from knowviz import ParserError as _ParserError

__author__ = "Daniel Rose"
__status__ = "Development"


def parse_document(fname: str, grammar: _pp.ParserElement, parse_all=True) -> list:
    """Open a document file and parse its content.

    Parameters:
    -----------
    path
        path/to/file
    grammar
        a pyparsing grammar to parse the file
    parse_all
        toggle whether the entire file should be parsed up to the end of file or not. Default: True

    Returns:
    --------
    results
        list of results
        """

    try:
        results = grammar.parseFile(fname, parseAll=parse_all)
    except _pp.ParseException as e:
        raise _ParserError(f"Could not find any known keyword in file {fname}.\n"
                           "You can resolve this error by either adding an alias for a keyword in the index or by "
                           "reviewing the file and properly referencing known keywords.")

    return results


def read_yaml_file(fname: str) -> dict:
    """Load index of quantities and pseudonyms from a YAML file."""

    fname = _os.path.normpath(fname)
    from ruamel.yaml import YAML
    yaml = YAML()
    try:
        with open(fname, "r") as file:
            return dict(yaml.load(file))
    except TypeError as e:
        if "NoneType" in str(e):
            return dict()


def write_yaml_file(fname: str, content: _t.Iterable):
    """Write content to a yaml file"""
    fname = _os.path.normpath(fname)
    if not (fname.endswith(".yml") or fname.endswith(".yaml")):
        fname = _os.path.join(fname, ".yml")

    from ruamel.yaml import YAML
    yaml = YAML()

    with open(fname, "w+") as file:
        yaml.dump(content, file)


def md5_checksum(fname: str):
    """Compute md5 checksum of a file."""
    hasher = _md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_directory(dirname, extension="") -> _t.Iterator[str]:
    """Recursively scan directory and subdirectories for files with given file extension (default: '') """
    for file_or_dir in _os.listdir(dirname):
        file_or_dir = _os.path.normpath(_os.path.join(dirname, file_or_dir))
        if _os.path.isdir(file_or_dir):
            for file in scan_directory(file_or_dir, extension):
                yield file
        elif _os.path.isfile(file_or_dir) and file_or_dir.endswith(extension):
            yield file_or_dir
        else:
            continue


def startfile(filename: str, folder: str = ""):
    """Start a given file in default application from python."""
    import sys
    import os
    import subprocess

    filepath = os.path.abspath(folder + filename)

    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))
