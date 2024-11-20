import pytest

from aws_json_term_matcher.exceptions import ParsingError
from aws_json_term_matcher.matcher import parse_filter


# This test case a
test_cases = [
    # simple case
    '{ $.eventType = "UpdateTrail" }',
    # numeric values
    "{ $.bandwidth > 75 }",
    "{ $.latency < 50 }",
    "{ $.refreshRate >= 60 }",
    "{ $.responseTime <= 5 }",
    "{ $.errorCode = 400}",
    "{ $.errorCode != 500 }",
    "{ $.number[0] = 1e-3 }",
    "{ $.number[0] != 1e+3 }",
    # ip
    "{ $.sourceIPAddress != 123.123.* }",
    # array
    '{ $.arrayKey[0] = "value"}',
    # grouped and logic operation
    '{( $.eventType = "UpdateTrail") ||  (($.eventType = "UpdateTrail2") && ($.eventType[2] = "uts")) }',
    # real life sample with arn
    '{($.detail-type ="ShopUnavailable") && (($.resources[1] = "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd") || ($.resources[0] = "arn:aws:states:us-east-1:111222333444:stateMachine:OrderProcessorWorkflow"))}',
    '{ $.number[0][1]["test"].test = 1e-3 }',
    '{ ($.detail-type = "ShopUnavailable") && (($.resources[1] = "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd") || ($.resources[0] = "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd"))}'
]


@pytest.mark.parametrize("filter_definition", test_cases)
def test_parse_filter(filter_definition):
    result = parse_filter(filter_definition)
    assert result


error_cases = [
    "{}",
    "{",
    "{)",
    "{}",
    "{)}",
    '{ .attribute = "a"}',
    '{ $.attribute * "a"}',
    "{$[asdf] = 1}",
    "{$[0.1] = 1}",
    "$.attribute = 1",
    "{$.attribute = 1 &}",
    "{ || $.attribute = 1 }",
    "{($.attribute = 1 }",
    "{$.attribute = 1) }",
    "{($.attribute = 1) && () }",
]


@pytest.mark.parametrize("filter_definition", error_cases)
def test_error_message(filter_definition):
    with pytest.raises(ParsingError):
        parse_filter(filter_definition)
