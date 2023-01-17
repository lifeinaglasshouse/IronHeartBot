from random import randint
from .tagobj import TagType, TagException

def rand(*args: TagType):
    if len(args) != 2:
        raise TagException("rand function", f"required exact 2 arguments. Got {len(args)}")
    a, b = args
    if a.is_num() and b.is_num():
        return randint(int(a.v), int(b.v))
    raise TagException("rand function", "both argument must be number")

builtin_export = {
    "rand": TagType(rand)
}