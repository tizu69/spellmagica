# fmt: off
keywords = [
    "and",		"break",	"do",		"else",		"elseif",	"end",
    "false",	"for",		"function",	"goto",		"if",		"in",
    "local",	"nil",		"not",		"or",		"repeat",	"return",
    "then",		"true",		"until",	"while",
]
# fmt: on


def str(s: str) -> str:
    """Escape a string for Lua source code."""
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'
