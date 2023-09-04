import json

import fzf_json_viewer
import preview
import pytest

with open("test/test01.json") as f:
    test01_json = json.load(f)


@pytest.mark.parametrize(
    "j,expected",
    [
        (
            test01_json,
            [["top"], ["top", "[]", "key1"], ["top", "[]", "key2"]],
        ),
    ],
)
def test_collect_keys(j, expected):
    response = fzf_json_viewer.collect_keys(j)
    assert response == expected


@pytest.mark.parametrize(
    "file,expected",
    [
        ("test.json", "python preview.py test.json {+}"),
    ],
)
def test_get_preview(file, expected):
    response = fzf_json_viewer.get_preview(file)
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
        (".top|.[]|.key1", ".top|.[]|.key1", 14),
        (".top|.[]|.key1", ".top|.[]|.key2", 9),
        (".top|.[]|.key1", ".top|.[]|.key12", 9),
    ],
)
def test_common_prefix_length(a, b, expected):
    response = preview.common_prefix_length(a, b)
    print(a[:response] + " " + a[response:])
    assert response == expected
