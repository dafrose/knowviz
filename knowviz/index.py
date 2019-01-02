"""Creating and updating database indices."""
import os as _os
import typing as _t
from hashlib import md5 as _md5
import pyparsing as _pp


class ParserError(Exception):
    pass


def create_grammar(keywords: _t.Sequence) -> _pp.ParserElement:
    """Create a pyparsing grammar that matches keywords, ignoring the remainder of the text. Using `pyparsing.Keyword`
    and MatchFirst will match the first in the list of keywords as isolated words. The list of `keywords` will be sorted
    internally, such that longer strings are matched first (mimicking the behaviour of `pyparsing.oneOf`)."""
    keywords = list(keywords)
    keywords.sort(key=len, reverse=True)  # sort by descending length
    keywords = (_pp.Keyword(key) for key in keywords)
    keywords = _pp.MatchFirst(keywords)
    other_text = _pp.Suppress(_pp.SkipTo(keywords))
    line_end = _pp.Suppress(_pp.SkipTo(_pp.StringEnd()))
    grammar = _pp.OneOrMore(other_text + keywords) + line_end
    return grammar


def parse_tex_file(fname: str, grammar: _pp.ParserElement, parse_all=True) -> list:
    """Open a tex file and parse its content.

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

    if not fname.endswith(".tex"):
        fname = fname + ".tex"
    try:
        results = grammar.parseFile(fname, parseAll=parse_all)
    except _pp.ParseException as e:
        raise ParserError(f"Could not find any known keyword in file {fname}.\n"
                          "You can resolve this error by either adding an alias for a keyword in the index or by "
                          "reviewing the file and properly referencing known keywords.")

    return results


def load_yaml_file(fname: str) -> dict:
    """Load index of quantities and pseudonyms from a YAML file."""

    fname = _os.path.normpath(fname)
    from ruamel.yaml import YAML
    yaml = YAML()
    try:
        with open(fname, "r") as file:
            quantities = dict(yaml.load(file))
    except FileNotFoundError:
        quantities = dict()

    return quantities


def write_yaml_file(fname: str, content: _t.Iterable):
    """Write content to a yaml file"""
    fname = _os.path.normpath(fname)
    if not (fname.endswith(".yml") or fname.endswith(".yaml")):
        fname = _os.path.join(fname, ".yml")

    from ruamel.yaml import YAML
    yaml = YAML()

    with open(fname, "w+") as file:
        yaml.dump(content, file)


def find_keyword_references(fname, keywords: _t.Iterable):
    """Load a file (e.g. model) and find references to a given set of keywords."""

    keywords = list(keywords)
    grammar = create_grammar(keywords)
    results = list(parse_tex_file(fname, grammar))

    return results


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


def update_model_index(dirname: str):
    # load quantities index
    fname = _os.path.join(dirname, "metadata/", "quantities.yml")
    quantities = load_yaml_file(fname)
    keywords = list(quantities.keys())

    # load models index
    fname = _os.path.join(dirname, "metadata/", "models.yml")
    models = load_yaml_file(fname)

    # load all models in model directory
    model_dir = _os.path.join(dirname, "models/")
    changed = False
    for fname in scan_directory(model_dir, extension=".tex"):
        checksum = md5_checksum(fname)
        model, _ = _os.path.splitext(_os.path.split(fname)[-1])
        try:
            # see if model is already known and if checksum has been changed
            assert models[model]["checksum"] == checksum
        except (KeyError, AssertionError):
            # update/create model entry
            refs = find_keyword_references(fname, keywords)
            refs = tuple({quantities[ref] for ref in refs})
            models[model] = dict(checksum=checksum,
                                 keywords=refs)
            # note that model index has changed
            changed = True
        else:
            # model is known and checksum is identical
            continue

    # write changed index to file
    if changed:
        fname = _os.path.join(dirname, "metadata/", "models.yml")
        write_yaml_file(fname, models)

    return changed


def update_keyword_index(dirname: str, index_name: str) -> bool:

    # load quantities index
    index_fname = _os.path.join(dirname, "metadata/", f"{index_name}.yml")
    keywords = load_yaml_file(index_fname)

    changed = False
    # get list of filenames
    data_dir = _os.path.join(dirname, f"{index_name}/")
    for fname in scan_directory(data_dir, extension=".tex"):
        key, _ = _os.path.splitext(_os.path.split(fname)[-1])

        if key not in keywords:
            keywords[key] = key
            changed = True

    if changed:
        # overwrite yaml file
        write_yaml_file(index_fname, keywords)

    return changed


def update_quantity_index(dirname: str) -> bool:

    return update_keyword_index(dirname, "quantities")


def add_keyword_synonym(fname, keywords: dict, target: str, alternative: str):
    """Add a pseudonym to a keyword in the keywords index"""

    keywords[alternative] = target

    write_yaml_file(fname, keywords)
