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
    "HexItemT": _onlyHexable,
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
}


def native(t: str) -> bool:
    return t == _nativeLua


def get(t: str) -> str:
    if t.startswith("[") and t.endswith("]") and t.count("[") == 1:
        return f"{get(t[1:-1])}[]"
    unions = re.split(r"[/|]", t)
    output: list[str] = []
    for union in unions:
        union = union.strip().lower()
        monounion = union.endswith("s") and union[:-1] or union
        if union.endswith("?"):
            output.append(f"{get(union[:-1])} | nil")
        elif union.startswith("[") and union.endswith("]"):
            return f"{get(union[1:-1])}[]"
        elif union.startswith("list of "):
            output.append(f"({union[8:]})[]")
        elif union in hexTypes.keys():
            output.append(union)
        elif union in typeMap:
            output.append(typeMap[union])
        elif monounion in hexTypes.keys():
            output.append(monounion)
        elif monounion in typeMap:
            output.append(typeMap[monounion])
        else:
            if union not in alreadyLoggedMissingTypes:
                print(f"Unknown type: {union}", file=sys.stderr)
                alreadyLoggedMissingTypes.add(union)
            output.append(union)
    return f"({" | ".join(output)})"


def split(t: str) -> list[str]:
    t = re.sub(r"<[^>]*>", "", t.strip())
    nested = 0
    lastout = 0
    out: list[str] = []
    for i, c in enumerate(t):
        if c == "[" or c == "(":
            nested += 1
        elif c == "]" or c == ")":
            nested -= 1
        elif c == "," and nested == 0:
            out.append(t[lastout:i].strip())
            lastout = i + 1
    out.append(t[lastout:].strip())
    return out
