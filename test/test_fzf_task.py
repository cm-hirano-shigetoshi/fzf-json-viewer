import pytest
import src.fzf
import src.fzf_task


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
            [
                ["."],
                [".top"],
                [".top", ".[]", ".key1"],
                [".top", ".[]", ".key2"],
            ],
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
                ["."],
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
def test_get_src_list(j, expected):
    response = src.fzf_task._get_src_list(j)
    assert response == expected


@pytest.mark.parametrize(
    "options, expected",
    [
        (
            {"--reverse": True, "--preview": "date"},
            ["--reverse", "--preview", "date"],
        ),
    ],
)
def test_get_cmd_list_from_options(options, expected):
    response = src.fzf._get_cmd_list_from_options(options)
    assert response == expected
