"""Function to handle citations in markdown
"""
import typing as _t
import pyparsing as _pp

__author__ = "Daniel Rose"
__status__ = "Development"


def find_citations(filename: str):
    """Find citations in a file specified by `path`"""
    # create grammar

    # grammar: \cite{content}
    start = _pp.Suppress(r"\cite{")
    end = _pp.Suppress("}")
    reference = _pp.Word(_pp.alphas, _pp.alphanums + "." + "-" + "_")

    citation = start + reference + end

    skip = _pp.Suppress(_pp.SkipTo(start))

    grammar = _pp.ZeroOrMore(skip + citation)

    return grammar.parseFile(filename)

