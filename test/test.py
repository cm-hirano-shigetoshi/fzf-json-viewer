import fzf_options
import pytest

INPUT_JSON = {
    "top": [
        {
            "key1": "value11",
            "key2": "value21",
            "key3": "value31",
            "key4": "value41",
            "key5": "value51",
        },
        {
            "key1": "value12",
            "key2": "value22",
            "key3": "value32",
            "key4": "value42",
            "key5": "value52",
        },
    ]
}


@pytest.mark.parametrize(
    "lines,selector,selected,expected",
    [
        (
            [
                [".top"],
                [".top", ".[]", ".key1"],
                [".top", ".[]", ".key2"],
                [".top", ".[]", ".key3"],
                [".top", ".[]", ".key4"],
                [".top", ".[]", ".key5"],
            ],
            ".top|.[]|.key3",
            "value32",
            [
                [".top"],
                [".top", ".[]", 'select(.key3=="value32")', ".key1"],
                [".top", ".[]", 'select(.key3=="value32")', ".key2"],
                [".top", ".[]", 'select(.key3=="value32")', ".key3"],
                [".top", ".[]", 'select(.key3=="value32")', ".key4"],
                [".top", ".[]", 'select(.key3=="value32")', ".key5"],
            ],
        ),
    ],
)
def test_get_select_condition_list(lines, selector, selected, expected):
    response = fzf_options.get_select_condition_list(lines, selector, selected)
    assert response == expected


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
            [[".top"], [".top", ".[]", ".key1"], [".top", ".[]", ".key2"]],
        ),
        (
            {
                "top": [
                    {
                        "key1": "value11",
                        "key2": "value21",
                        "key3": "value31",
                        "key4": "value41",
                        "key5": "value51",
                    },
                    {
                        "key1": "value12",
                        "key2": "value22",
                        "key3": "value32",
                        "key4": "value42",
                        "key5": "value52",
                    },
                ]
            },
            [
                [".top"],
                [".top", ".[]", ".key1"],
                [".top", ".[]", ".key2"],
                [".top", ".[]", ".key3"],
                [".top", ".[]", ".key4"],
                [".top", ".[]", ".key5"],
            ],
        ),
    ],
)
def test_collect_keys(j, expected):
    response = fzf_options.collect_keys(j)
    assert response == expected


@pytest.mark.parametrize(
    "script_dir,port,expected",
    [
        (".", 12345, "python ./preview.py selected 12345 {+} | cat -n"),
    ],
)
def test_get_preview(script_dir, port, expected):
    response = fzf_options.get_preview(port, script_dir=script_dir)
    assert response == expected


@pytest.mark.parametrize(
    "keys,expected",
    [
        (
            [[".top"], [".top", ".[]", ".key1"], [".top", ".[]", ".key2"]],
            [".top", ".top|.[]|.key1", ".top|.[]|.key2"],
        ),
        (
            [[".top", ".[]", 'select(.key3=="value32")', ".key3"]],
            ['.top|.[]|select(.key3=="value32")|.key3'],
        ),
    ],
)
def test_get_key_list(keys, expected):
    response = fzf_options.get_key_list(keys)
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
    response = fzf_options.common_prefix_length([a, b])
    assert response == expected


@pytest.mark.parametrize(
    "a,b,c,expected",
    [
        (
            [".top", ".[]", ".key1"],
            [".top", ".[]", ".key2"],
            [".top", ".[]", ".key2", ".[]", ".hoge"],
            2,
        ),
    ],
)
def test_common_prefix_length_3(a, b, c, expected):
    response = fzf_options.common_prefix_length([a, b, c])
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
    response = fzf_options.make_query(pos, [a, b])
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
    response = fzf_options.make_query(pos, [a, b, c])
    assert response == expected


@pytest.mark.parametrize(
    "input_json,items,expected",
    [
        (
            INPUT_JSON,
            [".top|.[]|.key1"],
            '"value11"\n"value12"',
        ),
        (
            INPUT_JSON,
            [".top|.[]|.key1", ".top|.[]|.key2"],
            '["value11","value21"]\n["value12","value22"]',
        ),
    ],
)
def test_get_selected_part(input_json, items, expected):
    response = fzf_options.get_selected_part_text(input_json, items)
    assert response == expected


@pytest.mark.parametrize(
    "selector,specified,expected",
    [
        (
            ".top|.[]|.key1",
            "value12",
            '{top: [.top|.[]|select(.key1 == "value12")]}',
        ),
    ],
)
def test_get_filter_query(selector, specified, expected):
    response = fzf_options.get_filter_query_text(selector, specified)
    assert response == expected


@pytest.mark.parametrize(
    "input_json,selector,specified,expected",
    [
        (
            INPUT_JSON,
            ".top|.[]|.key1",
            "value12",
            {
                "top": [
                    {
                        "key1": "value12",
                        "key2": "value22",
                        "key3": "value32",
                        "key4": "value42",
                        "key5": "value52",
                    },
                ]
            },
        ),
    ],
)
def test_get_filtered_json(input_json, selector, specified, expected):
    response = fzf_options.get_filtered_json(input_json, selector, specified)
    assert response == expected
