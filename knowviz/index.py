"""Creating and updating database indices."""
from typing import Sequence

import pyparsing as pp


def create_grammar(keywords: Sequence) -> pp.ParserElement:
    """Create a pyparsing grammar that matches keywords, ignoring the remainder of the text."""
    keywords = (pp.Keyword(key) for key in keywords)
    keywords = pp.MatchFirst(keywords)
    other_text = pp.Suppress(pp.SkipTo(keywords))
    line_end = pp.Suppress(pp.SkipTo(pp.StringEnd()))
    grammar = pp.OneOrMore(other_text + keywords) + line_end
    return grammar


def parse_tex_file(path: str, grammar: pp.ParserElement, parse_all=True) -> list:
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

    if not path.endswith(".tex"):
        path = path + ".tex"

    results = grammar.parseFile(path, parseAll=parse_all)

    return results
