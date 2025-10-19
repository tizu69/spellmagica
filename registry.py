from typing_extensions import TypedDict
import json


class Operator(TypedDict):
    description: str
    inputs: str | None
    outputs: str | None
    book_url: str
    mod_id: str


class Pattern(TypedDict):
    id: str
    name: str
    direction: str
    signature: str
    is_per_world: bool
    operators: list[Operator]


class Registry(TypedDict):
    patterns: dict[str, Pattern]


def get() -> Registry:
    with open("registry.json", "r") as f:
        return Registry(json.load(f))
