import re

from brigid.library.entities import Page
from brigid.validation.entities import Error

UNORDERED_LIST_LINE_RE = re.compile(r"^\s*[-*+]\s+")
ORDERED_LIST_LINE_RE = re.compile(r"^\s*\d+\.\s+")


def is_list_line(line: str) -> bool:
    return bool(UNORDERED_LIST_LINE_RE.match(line)) or bool(ORDERED_LIST_LINE_RE.match(line))


def is_line_empty(line: str) -> bool:
    return not line.strip()


# TODO: what with nested lists?
# TODO: what with numbered lists?
# TODO: make difference for different list types (-, *, +, digit)
def parser(text: str) -> bool:  # noqa: CCR001

    is_in_list = False

    can_has_problem = False

    for line in text.split("\n"):
        if is_list_line(line):
            if can_has_problem:
                return True

            is_in_list = True
            continue

        if is_line_empty(line) and is_in_list:
            can_has_problem = True
            continue

        is_in_list = False
        can_has_problem = False

    return False


def page_has_correct_list_formatting(page: Page) -> list[Error]:
    if not parser(page.body):
        return []

    return [Error(filepath=page.path, message="Page has incorrect list formatting")]
