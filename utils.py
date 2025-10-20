def pascal(snake: str):
    return "".join(x.capitalize() for x in snake.lower().split("_"))


def camel(snake: str):
    psc = pascal(snake)
    return psc[0].lower() + psc[1:]
