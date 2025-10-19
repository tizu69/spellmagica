def camel(snake: str):
    cstr = "".join(x.capitalize() for x in snake.lower().split("_"))
    return cstr[0].lower() + cstr[1:]
