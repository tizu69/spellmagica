import re
import sys

alreadyLoggedMissingTypes: set[str] = set()

_onlyHexable = "userdata"
_nativeLua = "_nativeLua"
hexTypes = {
    ## Hexcasting
    "any": _nativeLua,
    "nil": _nativeLua,
    "HexGarbage": "{ garbage: true }",
    "number": _nativeLua,
    "boolean": _nativeLua,
    "HexVector": "{ x: number, y: number, z: number }",
    # "HexList": "any[]",?
    "HexEntity": "{ uuid: string, name: string|nil }",
    "HexPlayer": "{ isPlayer: true, uuid: string, name: string }",
    "HexPattern": "{ startDir: string, angles: string }",
    ## Other mods
    "HexIotaT": "{ iotaType: string }",
    "HexEntityT": "{ entityType: string }",
    "HexGate": "{ gate: string }",
    "HexMote": "{ moteUuid: string, itemID: string, nexusUuid: string|nil }",
    "string": _nativeLua,
    "HexMatrix": "{ col: number, row: number, matrix: any[] }",
    ## Only hexable types
    "HexComplex": _onlyHexable,
    "HexJump": _onlyHexable,
    "HexLong": _onlyHexable,
    "HexJson": _onlyHexable,
    "HexRoom": _onlyHexable,
    "HexMap": _onlyHexable,
    "HexText": _onlyHexable,
    "HexQuaternion": _onlyHexable,
    "HexIdentifier": _onlyHexable,
    "HexExpression": _onlyHexable,
    "HexItem": _onlyHexable,
    "HexItemT": _onlyHexable,
    "HexMarker": _onlyHexable,
    "HexDye": _onlyHexable,
    "HexPigment": _onlyHexable,
}

typeMap = {
    "entity": "HexEntity",
    "vec": "HexVector",
    "vec3": "HexVector",
    "vector": "HexVector",
    "num": "number",
    "int": "number",
    "list": "any[]",
    "complex": "HexComplex",
    "jump": "HexJump",
    "long": "HexLong",
    "str": "string",
    "0-20": "number",
    "0-24": "number",
    "null": "nil",
    "room": "HexRoom",
    "bool": "boolean",
    "map": "HexMap",
    "mat": "HexMatrix",
    "matrix": "HexMatrix",
    "mote": "HexMote",
    "gate": "HexGate",
    "text": "HexText",
    "qtrn": "HexQuaternion",
    "qrtn": "HexQuaternion",
    "quat": "HexQuaternion",
    "quaternion": "HexQuaternion",
    "pattern": "HexPattern",
    "int ≥ 0": "number",
    "player entity": "HexPlayer",
    "entity entity": "HexEntity",
    "identifier": "HexIdentifier",
    "identifiable": "HexVector",
    "any iota": "any",
    "player": "HexPlayer",
    "expression": "HexExpression",
    "expr": "HexExpression",
    "entitytype": "HexEntityT",
    "itemtypable": "(HexEntity|HexVector)",
    "itemtype": "HexItemT",
    "iotatype": "HexIotaT",
    "pos": "HexVector",
    "marker": "HexMarker",
    "dye": "HexDye",
    "item entity": "HexEntity",
    "speck entity": "HexEntity",
    "non-list": "any",
    "pigment": "HexPigment",
    "key": "(HexEntity|HexVector)",
    "villager": "HexEntity",
    "_hexalVillager": "[[HexItemT, number][], [HexItemT, number]]",
    "item stack": "HexItem",
    "item frame": "HexEntity",
    "iota": "any",
}


def native(t: str) -> bool:
    return t == _nativeLua


def split(t: str) -> list[str]:
    t = re.sub(r"<[^>]*>", "", t.strip())
    nested = 0
    lastout = 0
    out: list[str] = []
    for i, c in enumerate(t):
        if c in "[(":
            nested += 1
        elif c in "])":
            nested -= 1
        elif c == "," and nested == 0:
            out.append(t[lastout:i].strip())
            lastout = i + 1
    out.append(t[lastout:].strip())
    return [s for s in out if s]  # Filter empty strings


def get(t: str) -> str:
    # - Optional types: entity?
    # - Unions: entity | number, entity/number (checked first!)
    # - Arrays: [entity], [[entity]]
    # - Tuples: (entity, number)
    # - List syntax: list of entity
    # - Iota types with plural forms
    t = t.strip().lower()

    # https://hexal.hexxy.media/v/0.3.0/1.0/en_us/#patterns/spells/motes@hexal:mote/trade/get
    if t == "[complicated!]":
        return typeMap["_hexalVillager"]

    if not t:
        return "any"

    if t.endswith("?"):
        inner = get(t[:-1])
        return f"{inner} | nil"

    union_pos = _find_top_level_union(t)
    if union_pos is not None:
        unions = _split_on_union(t)
        union_types = [get(u.strip()) for u in unions if u.strip()]
        if len(union_types) == 1:
            return union_types[0]
        return f"({' | '.join(union_types)})"

    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        if not inner:
            return "any[]"

        parts = split(inner)
        if len(parts) > 1:
            inner_types = [get(part) for part in parts]
            return f"[{', '.join(inner_types)})]"  # tuple
        else:
            return f"({get(inner)})[]"

    if t.startswith("(") and t.endswith(")"):
        inner = t[1:-1].strip()
        if _has_top_level_comma(inner):
            parts = split(inner)
            inner_types = [get(part) for part in parts]
            return f"[{', '.join(inner_types)}]"
        else:
            return get(inner)

    if t.startswith("list of "):
        inner = t[8:].strip()
        return f"{get(inner)}[]"
    if t.endswith(" or null"):
        inner = t[:-8].strip()
        return f"{get(inner)} | nil"

    return _resolve_iota(t)


def _has_top_level_comma(t: str) -> bool:
    nested = 0
    for c in t:
        if c in "[(":
            nested += 1
        elif c in "])":
            nested -= 1
        elif c == "," and nested == 0:
            return True
    return False


def _find_top_level_union(t: str) -> int | None:
    nested = 0
    for i, c in enumerate(t):
        if c in "[(":
            nested += 1
        elif c in "])":
            nested -= 1
        elif c in "|/" and nested == 0:
            return i
    return None


def _split_on_union(t: str) -> list[str]:
    nested = 0
    lastout = 0
    out: list[str] = []

    for i, c in enumerate(t):
        if c in "[(":
            nested += 1
        elif c in "])":
            nested -= 1
        elif c in "|/" and nested == 0:
            out.append(t[lastout:i].strip())
            lastout = i + 1

    out.append(t[lastout:].strip())
    return [s for s in out if s]


def _resolve_iota(t: str) -> str:
    if t in hexTypes:
        return t
    if t in typeMap:
        return typeMap[t]

    if t.endswith("s") and len(t) > 1:
        if t.endswith("ies") and len(t) > 3:
            singular = t[:-3] + "y"
            if singular in hexTypes:
                return singular
            if singular in typeMap:
                return typeMap[singular]
        singular = t[:-1]
        if singular in hexTypes:
            return singular
        if singular in typeMap:
            return typeMap[singular]

    if t not in alreadyLoggedMissingTypes:
        print(f"Unknown type: {t}", file=sys.stderr)
        alreadyLoggedMissingTypes.add(t)

    return t
