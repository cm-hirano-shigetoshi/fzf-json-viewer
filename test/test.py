import fzf_json_viewer
import preview
import pytest


@pytest.mark.parametrize(
    "j,expected",
    [
        (
            {
                "top": [
                    {"key1": "value11", "key2": "value21"},
                    {"key1": "value12", "key2": "value22"},
                ]
            },
            [["top"], ["top", "[]", "key1"], ["top", "[]", "key2"]],
        ),
    ],
)
def test_collect_keys(j, expected):
    response = fzf_json_viewer.collect_keys(j)
    assert response == expected


@pytest.mark.parametrize(
    "file,script_dir,expected",
    [
        ("test.json", ".", "python ./preview.py test.json {+} | cat -n"),
    ],
)
def test_get_preview(file, script_dir, expected):
    response = fzf_json_viewer.get_preview(file, script_dir=script_dir)
    assert response == expected


@pytest.mark.parametrize(
    "keys,expected",
    [
        (
            [["top"], ["top", "[]", "key1"], ["top", "[]", "key2"]],
            ".top\n.top|.[]|.key1\n.top|.[]|.key2",
        ),
    ],
)
def test_get_key_list(keys, expected):
    response = fzf_json_viewer.get_key_list(keys)
    assert response == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ([".top", ".[]", ".key1"], [".top", ".[]", ".key1"], 3),
        ([".top", ".[]", ".key1"], [".top", ".[]", ".key2"], 2),
        ([".top", ".[]", ".key1"], [".top", ".[]", ".key12"], 2),
    ],
)
def test_common_prefix_length_2(a, b, expected):
    response = preview.common_prefix_length([a, b])
    assert response == expected


@pytest.mark.parametrize(
    "a,b,c,expected",
    [
        (
            [".top", ".[]", ".key1"],
            [".top", ".[]", ".key2"],
            [".top", ".[]", ".key2", "[]", "hoge"],
            2,
        ),
    ],
)
def test_common_prefix_length_3(a, b, c, expected):
    response = preview.common_prefix_length([a, b, c])
    assert response == expected


@pytest.mark.parametrize(
    "pos,a,b,expected",
    [
        (
            2,
            [".top", ".[]", ".key1"],
            [".top", ".[]", ".key2"],
            ".top|.[]|[(.key1),(.key2)]",
        ),
        (
            0,
            [".top", ".[]", ".key1"],
            [".aaa", ".[]", ".key2"],
            "[(.top|.[]|.key1),(.aaa|.[]|.key2)]",
        ),
    ],
)
def test_make_query_2(pos, a, b, expected):
    response = preview.make_query(pos, [a, b])
    assert response == expected


@pytest.mark.parametrize(
    "pos,a,b,c,expected",
    [
        (
            2,
            [".top", ".[]", ".key1"],
            [".top", ".[]", ".key2"],
            [".top", ".[]", ".key3"],
            ".top|.[]|[(.key1),(.key2),(.key3)]",
        ),
    ],
)
def test_make_query_3(pos, a, b, c, expected):
    response = preview.make_query(pos, [a, b, c])
    assert response == expected
