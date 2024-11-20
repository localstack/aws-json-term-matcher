import json
import pytest
from aws_json_term_matcher.matcher import match

EXAMPLE_JSON_EVENT = json.loads(
    """
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
"""
)


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
]


@pytest.mark.parametrize("filter_def, result", filters)
def test_matcher(filter_def, result):
    assert match(EXAMPLE_JSON_EVENT, filter_def) == result
