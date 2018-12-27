"""Creating and updating database indices."""
import os
import typing as _t
from hashlib import md5 as _md5
import pyparsing as _pp


def create_grammar(keywords: _t.Sequence) -> _pp.ParserElement:
    """Create a pyparsing grammar that matches keywords, ignoring the remainder of the text."""
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

    results = grammar.parseFile(fname, parseAll=parse_all)

    return results


def load_yaml_file(fname: str) -> dict:
    """Load index of quantities and pseudonyms from a YAML file."""

    from ruamel.yaml import YAML
    yaml = YAML()

    with open(fname, "r") as file:
        quantities = dict(yaml.load(file))

    return quantities


def write_yaml_file(fname: str, content: _t.Iterable):
    """Write content to a yaml file"""

    if not (fname.endswith(".yml") or fname.endswith(".yaml")):
        fname = os.path.join(fname, ".yml")

    from ruamel.yaml import YAML
    yaml = YAML()

    with open(fname, "w") as file:
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
    for file_or_dir in os.listdir(dirname):
        path = os.path.join(dirname, file_or_dir)
        if os.path.isdir(path):
            for file in scan_directory(path):
                yield file
        elif os.path.isfile(path) and file_or_dir.endswith(extension):
            yield path
        else:
            continue


def update_model_index(dirname: str):
    # load quantities index
    fname = os.path.join(dirname, "metadata/", "quantities.yml")
    quantities = load_yaml_file(fname)
    keywords = list(quantities.keys())

    # load models index
    fname = os.path.join(dirname, "metadata/", "models.yml")
    models = load_yaml_file(fname)

    # load all models in model directory
    model_dir = os.path.join(dirname, "models/")
    changed = False
    for fname in scan_directory(model_dir, extension=".tex"):
        checksum = md5_checksum(fname)
        model = fname.split("/")[-1].split(".")[0]
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
        fname = os.path.join(dirname, "metadata/", "models.yml")
        write_yaml_file(fname, models)

    return changed


def update_keyword_index(dirname: str, index_name: str = "quantities") -> bool:

    # load quantities index
    index_fname = os.path.join(dirname, "metadata/", f"{index_name}.yml")
    keywords = load_yaml_file(index_fname)

    changed = False
    # get list of filenames
    data_dir = os.path.join(dirname, f"{index_name}/")
    for fname in scan_directory(data_dir, extension=".tex"):
        key = fname.split("/")[-1].split(".")[0]

        if key not in keywords:
            keywords[key] = key
            changed = True

    if changed:
        # overwrite yaml file
        write_yaml_file(index_fname, keywords)

    return changed


def add_alternative_keyword(fname, keywords: dict, target: str, alternative: str):
    """Add a pseudonym to a keyword in the keywords index"""

    keywords[alternative] = target

    write_yaml_file(fname, keywords)
