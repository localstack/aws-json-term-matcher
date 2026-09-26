import json

import pytest

from aws_json_term_matcher.matcher import match

EXAMPLE_JSON_EVENT = json.loads("""
{
    "eventType": "UpdateTrail",
    "bandwidth": 80,
    "latency": 30,
    "refreshRate": 60,
    "responseTime": 4,
    "errorCode": 400,
    "number": [1e-3, 1000],
    "sourceIPAddress": "123.123.456.789",
    "arrayKey": ["value", "anotherValue"],
    "eventTypeList": ["UpdateTrail", "UpdateTrail2", "uts"],
    "detail-type": "ShopUnavailable",
    "resources": [
        "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd",
        "arn:aws:states:us-east-1:111222333444:stateMachine:OrderProcessorWorkflow"
    ]
}
""")


filters = [
    # Numeric value filter
    ("{ $.bandwidth > 80 }", False),
    ("{ $.bandwidth = 80 }", True),
    ("{ $.bandwidth < 80 }", False),
    ("{ $.refreshRate >= 60 }", True),
    ("{ $.refreshRate <= 60 }", True),
    # Scientific notation
    # ("{ $.number[0] = 1e-3}", True),
    # Text value filter
    ('{ $["eventType"] = "UpdateTrail" }', True),
    ('{ $["eventType"] = "UpdateTrail2" }', False),
    ('{ $["eventType"] != "UpdateTrail" }', False),
    ('{ $["eventType"] != "UpdateTrail2" }', True),
    ('{ $["eventTypeList"][2] = "uts" }', True),
    # Ip value filter
    ("{ $.sourceIPAddress = 123.* }", True),
    ("{ $.sourceIPAddress = 10.0.1.0 }", False),
    ("{ $.sourceIPAddress != 10.0.1.0 }", True),
    # AND op
    ("{ $.bandwidth = 80 && $.refreshRate >= 60}", True),
    ("{ $.bandwidth != 80 && $.refreshRate >= 60}", False),
    # OR op
    ("{ $.bandwidth = 80 || $.refreshRate >= 60}", True),
    ("{ $.bandwidth != 80 || $.refreshRate >= 60}", True),
    ("{ $.bandwidth != 80 || $.refreshRate != 60}", False),
    # Grouped
    ("{ ($.bandwidth = 80) || ($.refreshRate >= 60)}", True),
    ("{ ($.bandwidth = 80 || $.refreshRate >= 60)}", True),
    ("{ $.bandwidth = 80 && ($.refreshRate >= 60)}", True),
    # Non existent attributes
    ("{ $.non-existent = 80 }", False),
    ('{ $["non-existent"] = 80 }', False),
    ('{ $["number"][4]= 80 }', False),
    # Complex search
    (
        '{ ($.detail-type = "ShopUnavailable") && (($.resources[1] = "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd") || ($.resources[0] = "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd"))}',
        True,
    ),
    # Special cases
    ('{$.eventType = "*"}', True),
    # NOT EXISTS / NOT EXIST
    ("{ $.SomeOtherObject NOT EXISTS }", True),
    ("{ $.SomeOtherObject NOT EXIST }", True),
    ("{ $.SomeOtherObject not exists }", True),
    ("{ $.SomeOtherObject not exist }", True),
    ("{ $.eventType NOT EXISTS }", False),
    ("{ $.eventType NOT EXIST }", False),
    ('{ $["eventType"] NOT EXISTS }', False),
    ('{ $["non-existent"] NOT EXISTS }', True),
    ("{ $.number[0] NOT EXISTS }", False),
    ("{ $.number[4] NOT EXISTS }", True),
    ("{ $.non_existent.nested NOT EXISTS }", True),
    ('{($.SomeOtherObject NOT EXISTS) && ($.eventType = "UpdateTrail")}', True),
    ('{($.SomeOtherObject NOT EXISTS) && ($.eventType != "UpdateTrail")}', False),
    ("{ $.SomeOtherObject NOT EXISTS || $.bandwidth = 999 }", True),
    ("{ $.eventType NOT EXISTS || $.bandwidth = 999 }", False),
]


@pytest.mark.parametrize("filter_def, result", filters)
def test_matcher(filter_def, result):
    assert match(EXAMPLE_JSON_EVENT, filter_def) == result


def test_not_exists_with_null_and_nested():
    data = {
        "nullable": None,
        "nested": {"present": "value", "null_child": None},
        "empty_list": [],
    }
    # An attribute with value null (None) exists, so NOT EXISTS is False
    assert match(data, "{ $.nullable NOT EXISTS }") is False
    assert match(data, "{ $.nested.null_child NOT EXISTS }") is False
    # An attribute that does not exist
    assert match(data, "{ $.missing NOT EXISTS }") is True
    assert match(data, "{ $.missing NOT EXIST }") is True
    assert match(data, "{ $.nested.missing NOT EXISTS }") is True
    assert match(data, "{ $.missing.deeply.nested NOT EXISTS }") is True
    assert match(data, "{ $.empty_list[0] NOT EXISTS }") is True
    # Non-existent attribute with comparison returns False without error
    assert match(data, '{ $.missing = "value" }') is False
    assert match(data, '{ $.missing.nested = "value" }') is False
