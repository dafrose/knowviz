"""Creating and updating database indices."""
import os as _os
import typing as _t
import pyparsing as _pp

from knowviz.io import parse_document, read_yaml_file, write_yaml_file, md5_checksum, scan_directory


class Index(dict):

    def __init__(self, filename: str = "", datadir: str = "", **kwargs):

        if filename is not "":
            super().__init__(read_yaml_file(filename), **kwargs)
        else:
            super().__init__(**kwargs)

        self.filename = filename
        self.datadir = datadir

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
        write_yaml_file(self.filename, dict(self))

    def rescan_documents(self):
        raise NotImplementedError


class KeywordIndex(Index):

    def unique_keys(self) -> _t.Iterator:
        """Iterator of unique keys in the keyword index, i.e. keys that refer to themselves rather than others."""
        return (key for key, value in self.items() if isinstance(value, dict))

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

    def rescan_documents(self) -> bool:
        """Scan through documents given in `datadir` (and below)."""
        changed = False
        # get list of filenames
        if self.datadir is "":
            # default to data directory based on index name
            self.datadir = _os.path.join(self.basedir, self.name)
        for fname in scan_directory(self.datadir, extension=".yml"):
            checksum = md5_checksum(fname)
            keyword, _ = _os.path.splitext(_os.path.split(fname)[-1])

            try:
                # see if key is already known and if checksum has been changed
                assert self[keyword]["checksum"] == checksum
            except (KeyError, AssertionError, TypeError):
                # index will be changed
                changed = True
                # load keyword data into index
                keyword_info = read_yaml_file(fname)
                for synonym in keyword_info["synonyms"]:
                    self[synonym] = keyword

                # save new checksum and relative path of file
                relpath = _os.path.relpath(fname, self.datadir)
                relpath.replace("\\", "/")
                self[keyword] = dict(checksum=checksum,
                                     file=relpath)

        if changed:
            print(f"Updated '{self.name}' index.")
        else:
            print(f"No changes detected.")
        return changed


class RelationIndex(Index):

    def __init__(self, keyword_index: KeywordIndex, filename: str = "",
                 datadir: str = "", data_file_ext: str = "",
                 **kwargs):
        """
        Index type for relations between keywords. Parses document files to collect keyword mentions. One document
        corresponds to one relation.

        Parameters
        ----------
        keyword_index
            Reference to an instance of KeywordIndex. Relations will be established between keys defined in this index.
        filename
            (Optional) path/to/file to load previous index data from.
        datadir
            (Optional) relative or absolute path to directory that contains the documents that this index relates to.
            Default directory is defined by the index filename as given in `filename`
        data_file_ext
            (Optional) file extension of documents related to this index. If none is given, the index will search
            through all files in `datadir` (and below).
        kwargs
            (Optional) keyword arguments that are passed on to the `dict` constructor (will become dictionary entries).
        """

        super().__init__(filename, datadir, **kwargs)

        self.keywords = keyword_index
        self.data_file_ext = data_file_ext

    def rescan_documents(self) -> bool:
        """Update index from files in the database."""

        self.keywords.rescan_documents()

        if self.datadir is "":
            # default to data directory based on index name
            self.datadir = _os.path.join(self.basedir, self.name)
            # if no filename was specified, document will be scanned based on the current working directory

        # load all models in model directory / relations in relation directory
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

        return changed

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
