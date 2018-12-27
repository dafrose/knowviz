"""Test the indexing module."""

import pytest


@pytest.mark.parametrize(("text", "keywords", "expected"),
                         (("abc kij lasd def ölkl abc", ("abc", "def"), ["abc", "def", "abc"]),))
def test_create_grammar(text, keywords, expected):
    from knowviz.index import create_grammar

    grammar = create_grammar(keywords)
    result = grammar.parseString(text)

    assert list(result) == expected


@pytest.mark.parametrize(("path", "keywords", "expected"),
                         (("data/models/m1", ("q2", "q1"), ["q1", "q2"]),
                          ))
def test_parse_tex_file(path, keywords, expected):

    from knowviz.index import create_grammar, parse_tex_file

    grammar = create_grammar(keywords)
    # find without file extension
    results = list(parse_tex_file(path, grammar))
    assert results == expected

    # with file extension
    path = path + ".tex"
    results = list(parse_tex_file(path, grammar))
    assert results == expected
