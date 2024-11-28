# AWS JSON Term Matcher

`aws_json_term_matcher` is a Python package designed to parse and evaluate filter expressions, such as those found in AWS CloudWatch log filters. This tool uses **Lark** for PEG parsing and supports logical operations like `AND`, `OR`, and parentheses for grouping.

## Features
- Parses logical expressions from JSON filters
- Supports `&&` (AND), `||` (OR), and parentheses for nested expressions
- Extensible to include evaluation and tree reduction (future updates)

## Installation

Clone the repository and install the requirements:

```bash
pip install aws-json-term-matcher
```


## What does this tool do?

This tool provides enhanced JSON term matching for logs, giving you more flexibility and functionality when working with CloudWatch Logs. It allows you to use more sophisticated filters to search through JSON log events, making your log filtering more efficient.

The key improvement is the ability to filter logs with patterns similar to those used in AWS CloudWatch Logs but with more powerful Python-based features.

### Example

```python
from aws_json_term_matcher.matcher import match

# Example log
log = {
    "eventType": "UpdateTrail",
    "bandwidth": 80,
    "latency": 45,
    "number": [0.001, 1000],
    "sourceIPAddress": "123.123.1.1",
    "resources": [
        "arn:aws:states:us-east-1:111222333444:execution:OrderProcessorWorkflow:d57d4769-72fd",
        "arn:aws:states:us-east-1:111222333444:stateMachine:OrderProcessorWorkflow"
    ]
}

# Example filter
filter_str = '{ $.bandwidth > 75 }'


# Apply filter to log
if match(log, filter_str):
    print("Log matches the filter!")
else:
    print("Log does not match.")
```
In this example, the tool filters a log based on bandwidth and latency values, similar to how AWS CloudWatch Logs filters JSON log events.

### Documentation
For more information about the original JSON term matching feature in AWS CloudWatch Logs, check out the [official AWS documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html#matching-terms-json-log-events).

## Contributing

Contributions are welcome and appreciated! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.
