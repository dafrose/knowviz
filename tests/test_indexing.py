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


def test_load_quantities_index():

    from knowviz.index import load_yaml_file

    path = "data/metadata/quantities.yml"
    quantities = load_yaml_file(path)

    expected = dict(q1="q1", q2="q2", q_1="q1", q_2="q2")

    assert quantities == expected


def test_parse_keyword_reference():

    from knowviz.index import load_yaml_file
    quantities = set(load_yaml_file("data/metadata/quantities.yml"))

    path = "data/models/m1.tex"
    from knowviz.index import find_keyword_references

    results = set(find_keyword_references(path, quantities))
    for keyword in ["q1", "q2"]:
        assert keyword in results


def test_scan_directory():

    from knowviz.index import scan_directory

    files = scan_directory("data/models/", extension=".tex")

    assert next(files).endswith(".tex")


def test_md5_checksum():
    """Test md5 checksum computation and verify it is the same as in the models index."""

    from knowviz.index import md5_checksum, load_yaml_file

    checksum = md5_checksum("data/models/m1.tex")

    models = load_yaml_file("data/metadata/models.yml")

    # verify that checksum is identical.
    # if this fails, run the update_data.py script to update the models index.
    assert checksum == models["m1"]["checksum"]
