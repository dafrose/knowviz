"""Test the indexing module."""

import pytest


@pytest.mark.parametrize(("text", "keywords", "expected"),
                         (("abc kij lasd def ölkl abc", ("abc", "def"), ["abc", "def", "abc"]),))
def test_create_grammar(text, keywords, expected):
    from knowviz.index import RelationIndex

    grammar = RelationIndex.create_grammar(keywords)
    result = grammar.parseString(text)

    assert list(result) == expected


@pytest.mark.parametrize(("path", "keywords", "expected"),
                         (("data/models/m1", ("q2", "q1"), ["q1", "q2"]),
                          ))
def test_parse_tex_file(path, keywords, expected):
    from knowviz.index import RelationIndex
    from knowviz.io import parse_document

    grammar = RelationIndex.create_grammar(keywords)

    # with file extension
    path = path + ".tex"
    results = list(parse_document(path, grammar))
    assert results == expected


def test_load_quantities_index():
    from knowviz.io import read_yaml_file

    path = "data/metadata/quantities.yml"
    quantities = read_yaml_file(path)

    expected = dict(q1="q1", q2="q2", q_1="q1", q_2="q2", q3="q3")

    for key in expected:
        assert key in quantities

    assert len(quantities) == len(expected)


def test_get_unique_keys():
    """Test the unique_keys method of KeywordIndex"""

    from knowviz.index import KeywordIndex
    quantities = KeywordIndex("data/metadata/quantities.yml")
    expected = ("q1", "q2", "q3")

    count = 0
    for key in quantities.unique_keys():
        assert key in expected
        count += 1

    assert count == len(expected)

    uniques = tuple(quantities.unique_keys())
    assert uniques == expected


def test_parse_keyword_reference():
    from knowviz.index import RelationIndex, KeywordIndex

    quantities = KeywordIndex("data/metadata/quantities.yml")

    index = RelationIndex(quantities, data_file_ext=".tex")

    path = "data/models/m1.tex"
    results = set(index.find_keyword_references(path))
    for keyword in ["q1", "q2"]:
        assert keyword in results


@pytest.mark.parametrize("dirname", ("models", "quantities"))
def test_scan_directory(dirname):
    from knowviz.io import scan_directory

    files = scan_directory(f"data/{dirname}/", extension=".tex")

    for file in files:
        assert file.endswith(".tex")


def test_md5_checksum():
    """Test md5 checksum computation and verify it is the same as in the models index."""

    from knowviz.io import md5_checksum
    from knowviz.io import read_yaml_file

    checksum = md5_checksum("data/models/m1.tex")

    models = read_yaml_file("data/metadata/models.yml")

    # verify that checksum is identical.
    # if this fails, run the update_data.py script to update the models index.
    assert checksum == models["m1"]["checksum"]
