"""Creating and updating database indices."""
import os as _os
import typing as _t
import pyparsing as _pp

from knowviz.io import parse_document, read_yaml_file, write_yaml_file, md5_checksum, scan_directory


class Index(dict):

    def __init__(self, filename: str = "", datadir: str = "", data_file_ext: str = "", **kwargs):

        if filename is not "":
            super().__init__(read_yaml_file(filename), **kwargs)
        else:
            super().__init__(**kwargs)

        self.filename = filename
        self.datadir = datadir
        self.data_file_ext = data_file_ext

    @property
    def name(self):
        """Name of the index. Defined by filename."""
        name, _ = _os.path.splitext(_os.path.split(self.filename)[1])
        return name

    @property
    def indexdir(self):
        """Path to parent directory of this index (which is the assumed location of other indices)."""
        indexdir, _ = _os.path.split(self.filename)
        return indexdir

    @property
    def basedir(self):
        """Name of the index. Defined by filename."""
        basedir, _ = _os.path.split(self.indexdir)
        return basedir

    def save_to_file(self, filename: str = ""):
        """Save index to a yaml file. If no filename is given, will try to use already defined filename."""

        if filename is not "":
            self.filename = filename
        elif self.filename is "":
            raise ValueError("No filename defined. Please define a filename.")
        write_yaml_file(self.filename, self)

    def update(self, *args, **kwargs):

        if args or kwargs:
            super().update(*args, **kwargs)
        else:
            raise NotImplementedError


class KeywordIndex(Index):

    def unique_keys(self) -> _t.Iterator:
        """Iterator of unique keys in the keyword index, i.e. keys that refer to themselves rather than others."""
        return (key for key, value in self.items() if key == value)

    def synonyms(self) -> dict:
        """Dictionary with unique keys as key and a list of synonyms as values."""

        synonyms = dict()
        for key in self.unique_keys():
            synonyms[key] = []

        for key, value in self.items():
            if value in synonyms:
                if key != value:
                    synonyms[value].append(key)

        return synonyms

    def update(self, *args, **kwargs):
        """If any argument is given, it is passed to `dict.update`. Otherwise the index is update from files in the
        database."""

        if args or kwargs:
            super().update(*args, **kwargs)
        else:  # update from file
            changed = False
            # get list of filenames
            if self.datadir is "":
                # default to data directory based on index name
                self.datadir = _os.path.join(self.basedir, self.name)
            for fname in scan_directory(self.datadir, extension=self.data_file_ext):
                key, _ = _os.path.splitext(_os.path.split(fname)[-1])

                if key not in self:
                    self[key] = key
                    changed = True

            if changed:
                print(f"Updated {self.name} index.")
            else:
                print(f"No changes detected.")


class RelationIndex(Index):

    def __init__(self, keyword_index: KeywordIndex, filename: str = "",
                 datadir: str = "", data_file_ext: str = "",
                 **kwargs):

        super().__init__(filename, datadir, data_file_ext, **kwargs)

        self.keywords = keyword_index

    def update(self, *args, **kwargs):
        """If any argument is given, it is passed to `dict.update`. Otherwise the index is update from files in the
        database."""

        if args or kwargs:
            super().update(*args, **kwargs)
        else:
            self.keywords.update()

            # load all models in model directory
            if self.datadir is "":
                # default to data directory based on index name
                self.datadir = _os.path.join(self.basedir, self.name)

            changed = False
            for fname in scan_directory(self.datadir, extension=self.data_file_ext):
                checksum = md5_checksum(fname)
                model, _ = _os.path.splitext(_os.path.split(fname)[-1])
                try:
                    # see if model is already known and if checksum has been changed
                    assert self[model]["checksum"] == checksum
                except (KeyError, AssertionError):
                    # update/create model entry
                    refs = self.find_keyword_references(fname)
                    refs = tuple({self.keywords[ref] for ref in refs})
                    self[model] = dict(checksum=checksum,
                                       keywords=refs)
                    # note that model index has changed
                    changed = True
                else:
                    # model is known and checksum is identical
                    continue

            if changed:
                print(f"Updated {self.name} index.")
            else:
                print(f"No changes detected.")

    @staticmethod
    def create_grammar(keywords: _t.Iterable[str]) -> _pp.ParserElement:
        """Create a pyparsing grammar that matches keywords, ignoring the remainder of the text.."""
        keywords = _pp.oneOf(keywords, caseless=False)  # matches longest string first if substrings exist
        keywords = _pp.MatchFirst(keywords)
        other_text = _pp.Suppress(_pp.SkipTo(keywords))
        line_end = _pp.Suppress(_pp.SkipTo(_pp.StringEnd()))
        grammar = _pp.OneOrMore(other_text + keywords) + line_end
        return grammar

    def find_keyword_references(self, fname):
        """Load a file (e.g. model) and find references to a given set of keywords."""

        keywords = self.keywords.keys()
        grammar = self.create_grammar(keywords)
        results = list(parse_document(fname, grammar))

        return results
