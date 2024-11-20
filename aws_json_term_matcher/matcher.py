import os

from lark import Lark, Transformer, v_args, Tree, Token
from lark.exceptions import UnexpectedCharacters, UnexpectedInput, UnexpectedToken

from aws_json_term_matcher.exceptions import ParsingError, MatchingError


def extract_boolean(node):
    """
    Recursively traverse .children[0] until the value is a boolean.

    Args:
        node: The starting node to traverse.

    Returns:
        The boolean value once found.
    """
    while hasattr(node, "children") and node.children:
        node = node.children[0]
        if isinstance(node, bool):
            return node
    raise ValueError("No boolean value found in the node hierarchy.")


class IpRange:
    def __init__(self, ip_range: str):
        self.range = ip_range

    def ip_is_in_range(self, ip: str | None) -> bool:
        if ip is None:
            return False
        if len(ip) == 0:
            return False

        ip_parts = ip.split(".")
        range_parts = self.range.split(".")

        # Compare each part of the IP to the range
        for i in range(len(range_parts)):
            if range_parts[i] == "*":
                continue  # Wildcard matches any value
            if i >= len(ip_parts) or ip_parts[i] != range_parts[i]:
                return False
        return True


# Transformer to evaluate the parsed filter
@v_args(inline=True)
class FilterEvaluator(Transformer):
    def __init__(self, data):
        self.data = data

    def start(self, expr):
        if isinstance(expr, bool):
            return expr

        return extract_boolean(expr)

    def and_op(self, left, right):
        return extract_boolean(left) and extract_boolean(right)

    def or_op(self, left: Tree, right: Tree):
        return extract_boolean(left) or extract_boolean(right)

    def comparison(self, entity, comparator, value):
        entity_value = self.resolve_entity(entity)
        result = self.compare(entity_value, comparator, value)
        return result

    def resolve_entity(self, entity: Tree):
        # Extract the entity from the dictionary based on selection rules
        # This would resolve $.attribute or $[index] kind of paths in the dictionary
        keys = []
        # in this case the three only is composed of branch with just one branch
        # entity -> selection -> attribute access -> "NAME"

        def _resolve(node):
            if node.data == "attribute_access":
                # Handles attributes like $.attributeName or $["attributeName"]
                child = node.children[0]
                if child.type == "NAME":
                    keys.append(child.value)  # Regular attribute
                elif child.type == "ESCAPED_STRING":
                    keys.append(
                        child.value.strip('"')
                    )  # Attribute accessed like ["attr"]

            elif node.data == "index_access":
                index = node.children[0].value
                keys.append(index)

            elif node.data == "selection":
                # Keep recursing through the selection (attributes or indices)
                for child in node.children:
                    _resolve(child)
            elif node.data == "entity":
                for child in node.children:
                    _resolve(child)

        # Start traversing the entity tree to build the keys
        _resolve(entity)

        value = self.data
        try:
            for key in keys:
                if key.isdigit():
                    value = value[int(key)]
                else:
                    value = value.get(key, None)
            return value
        except IndexError:
            return None

    def compare(self, entity_value, comparator, value):
        comparator_value = comparator.value

        if isinstance(value, IpRange):
            return value.ip_is_in_range(entity_value)

        if comparator_value == "=":
            return entity_value == value
        elif comparator_value == "!=":
            return entity_value != value
        elif comparator_value == ">":
            return entity_value > value
        elif comparator_value == ">=":
            return entity_value >= value
        elif comparator_value == "<":
            return entity_value < value
        elif comparator_value == "<=":
            return entity_value <= value
        return False

    def value(self, value: Token):
        # Returns the value as-is (for STRING, NUMBER, etc.)
        if value.type in ["SCIENTIFIC", "NUMBER"]:
            return float(value.value)

        if value.type == "WILDCARD_IP":
            return IpRange(value.value)

        return value.value.strip("\"'")


def load_parser():
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar.lark")

    with open(grammar_path, "r") as grammar_file:
        grammar = grammar_file.read()
    return Lark(grammar, start="start", parser="lalr")


def parse_filter(expression):
    parser = load_parser()
    try:
        return parser.parse(expression)
    except (UnexpectedCharacters, UnexpectedInput, UnexpectedToken) as e:
        raise ParsingError(str(e))


def match(obj: dict, filter: str):
    tree = parse_filter(filter)
    evaluator = FilterEvaluator(obj)

    try:
        return evaluator.transform(tree)
    except Exception as e:
        raise MatchingError(str(e))
