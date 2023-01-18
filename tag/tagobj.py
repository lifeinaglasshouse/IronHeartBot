from typing import Callable

class TagException(Exception):
    
    def __init__(self, where: str, msg: str):
        self.where = where
        self.msg = msg
        super().__init__(f"In {where}, {msg}")

class TagObject:
    NAME = "object"

class TagNull(TagObject):
    NAME = "null"

class TagInt(TagObject):
    NAME = "integer"
    
    def __init__(self, v: int = 0) -> None:
        self.value = v

class TagFloat(TagObject):
    NAME = "float"
    
    def __init__(self, v: float = 0.0) -> None:
        self.value = v

class TagNativeFunc(TagObject):
    NAME = "NativeFunc"
    
    def __init__(self, name: str, func: Callable[[list[TagObject]], TagObject]) -> None:
        self.name = name
        self.func = func

class TagClass(TagObject):
    TYPE = None
    
    def __init__(self) -> None:
        self.fields: dict[str, TagRef] = {}
    
    def get_attr(self, name: str) -> 'TagRef':
        r = self.fields.get(name)
        if r is None:
            raise TagException("get attribute", f"{self.NAME} doesn't have '{name}' attribute")
        return r
    
    def has_attr(self, name: str) -> bool:
        return name in self.fields
    
    def repr(self) -> str:
        return f"[Instance of {self.NAME}]"

class TagStr(TagClass):
    NAME = "string"

    def __init__(self, v: str = "") -> None:
        super().__init__()
        self.value = v
        self.fields['__add__'] = TagRef(to_func(self.__add__))
        self.fields['__mul__'] = TagRef(to_func(self.__mul__))
        self.fields['__iter__'] = TagRef(to_func(self.__iter__))
        self.fields['__init__'] = TagRef(to_func(self._init_))
    
    def _init_(self, args: list[TagObject]):
        if len(args) != 1:
            return tag_null
        v = args[0]
        if is_num(v):
            self.value = str(v.value)
            return tag_null
        if is_str(v):
            self.value = v.value
            return tag_null
        if is_class(v) and v.has_attr('__str__'):
            r = tn_call(v.get_attr('__str__').v, [])
            if not is_str(r):
                raise TagException(f'{v.NAME}.__str__', f"must return string not {r.NAME}")
            self.value = r
        raise TagException(f'string.__init__', f"cannot convert {v.NAME} to string")
    
    def __add__(self, args: list[TagObject]):
        if len(args) != 1:
            raise TagException("string.__add__", "Required exact 1 argument")
        r = args[0]
        if is_str(r):
            return TagStr(self.value + r.value)
        raise TagException("string.__add__", f"first argument must be string not {r.NAME}")
    
    def __mul__(self, args: list[TagObject]):
        if len(args) != 1:
            raise TagException("string.__mul__", "Required exact 1 argument")
        r = args[0]
        if isinstance(r, TagInt):
            return TagStr(self.value + r.value)
        raise TagException("string.__mul__", f"first argument must be integer not {r.NAME}")
    
    def __iter__(self, args: list[TagObject]):
        if len(args) != 1:
            raise TagException("string.__iter__", "Required exact 1 argument")
        ctx = args[0]
        if isinstance(ctx, TagIterContext):
            if ctx.step >= len(self.value):
                ctx.is_end = True
                return TagStr('\0')
            return TagStr(self.value[ctx.step])
        raise TagException("string.__iter__", f"first argument must be IterationContext not {ctx.NAME}")
    
    def repr(self) -> str:
        return self.value

class TagIterContext(TagClass):
    NAME = "IterationContext"
    
    def __init__(self) -> None:
        super().__init__()
        self.step = 0
        self.is_end = False

class TagType(TagObject):
    
    def __init__(self, tclass: type[TagClass]) -> None:
        self.tclass = tclass
        self.tclass.TYPE = self
        self.NAME = tclass.NAME + " Type"
    
    def new(self, args: list[TagObject]) -> TagClass:
        c = self.tclass()
        if c.has_attr('__init__'):
            tn_call(c.fields['__init__'].v, args)
        return c

class TagRef:
    
    def __init__(self, v: TagObject) -> None:
        self.v = v

TagNumber = TagInt | TagFloat

def is_num(o: TagObject):
    return isinstance(o, TagNumber)

def is_str(o: TagObject):
    return isinstance(o, TagStr)

def is_null(o: TagObject):
    return isinstance(o, TagNull)

def is_callable(o: TagObject):
    return isinstance(o, TagNativeFunc)

def tn_add(l: TagNumber, r: TagNumber):
    rs = l.value + r.value
    return TagFloat(rs) if isinstance(rs, float) else TagInt(rs)

def tn_sub(l: TagNumber, r: TagNumber):
    rs = l.value - r.value
    return TagFloat(rs) if isinstance(rs, float) else TagInt(rs)

def tn_mul(l: TagNumber, r: TagNumber):
    rs = l.value * r.value
    return TagFloat(rs) if isinstance(rs, float) else TagInt(rs)

def tn_div(l: TagNumber, r: TagNumber):
    if r.value == 0:
        raise TagException("division", "division by zero is undefined")
    rs = l.value / r.value
    return TagFloat(rs)

def tn_eq(l: TagObject, r: TagObject):
    if is_num(l):
        if is_num(r):
            return TagInt(int(l.value == r.value))
    if is_str(l):
        if is_str(r):
            return TagInt(int(l.value == r.value))
    if is_class(l):
        return tn_mcall(l, "__eq__", r) or TagInt(0)
    return TagInt(0)

def tn_neq(l: TagObject, r: TagObject):
    return TagInt(int(not tn_eq(l, r).value))

def tn_gt(l: TagObject, r: TagObject):
    if is_num(l):
        if is_num(r):
            return TagInt(int(l.value > r.value))
    if is_class(l):
        return tn_mcall(l, "__gt__", r) or TagInt(0)
    return TagInt(0)

def tn_lt(l: TagObject, r: TagObject):
    if is_num(l):
        if is_num(r):
            return TagInt(int(l.value < r.value))
    if is_class(l):
        return tn_mcall(l, "__lt__", r) or TagInt(0)
    return TagInt(0)

def tn_ge(l: TagObject, r: TagObject):
    if is_num(l):
        if is_num(r):
            return TagInt(int(l.value >= r.value))
    if is_class(l):
        return tn_mcall(l, "__ge__", r) or TagInt(0)
    return TagInt(0)

def tn_le(l: TagObject, r: TagObject):
    if is_num(l):
        if is_num(r):
            return TagInt(int(l.value >= r.value))
    if is_class(l):
        return tn_mcall(l, "__le__", r) or TagInt(0)
    return TagInt(0)

def tn_pos(o: TagObject):
    if is_num(o):
        return o
    if is_class(o) and o.has_attr('__pos__'):
        return tn_call(tn_dot(o, "__pos__").v)
    raise TagException("unary +", f"{o.NAME} is not positiveable")

def tn_neg(o: TagObject):
    if is_num(o):
        return TagInt(-o.value)
    if is_class(o) and o.has_attr('__neg__'):
        return tn_call(tn_dot(o, "__neg__").v)
    raise TagException("unary -", f"{o.NAME} is not negateable")

def tn_not(o: TagObject):
    return bool2tbool(not tn_bool(o).value)

def tn_bool(o: TagObject):
    if is_num(o) or is_str(o):
        return TagInt(int(bool(o.value)))
    if is_null(o):
        return TagInt(0)
    if is_class(o) and o.has_attr('__bool__'):
        return tn_call(tn_dot(o, '__bool__').v, []) # doesn't guarantee it gonna return TagInt
    return TagInt(1)

def tbool2bool(o: TagObject):
    return bool(tn_bool(o).value)

def bool2tbool(o: bool):
    return TagInt(int(o))

def tn_and(l: TagObject, r: TagObject):
    return bool2tbool(tbool2bool(l) and tbool2bool(r))

def tn_or(l: TagObject, r: TagObject):
    return bool2tbool(tbool2bool(l) or tbool2bool(r))

def tn_call(c: TagNativeFunc, args: list[TagObject] | None = None):
    args = args or []
    if is_class(c) and c.has_attr('__call__'):
        return tn_call(c.get_attr("__call__").v, *args)
    if not is_callable(c):
        raise TagException(f"operation call", f"{c.NAME} is not callable")
    return c.func(args)

def tn_getv(o: TagNumber | TagStr):
    return o.value

def to_tnum(o: int | float):
    return TagFloat(o) if isinstance(o, float) else TagInt(o)

def to_func(o: Callable[[list[TagObject]], TagObject]):
    return TagNativeFunc(o.__name__, o)

def tn_repr(o: TagObject | None):
    if o is None:
        return o
    if is_num(o):
        return str(o.value)
    if is_str(o):
        return o.value
    if is_class(o):
        return o.repr()
    return f"[Instance of {o.NAME}]"

def is_class(o: TagObject):
    return isinstance(o, TagClass)

def tn_dot(l: TagObject, r: str) -> TagRef:
    if is_class(l):
        return l.get_attr(r)
    raise TagException("get attribute", f"{l.NAME} is an atomic type (doesn't have any attributes)")

def tn_mcall(l: TagClass, m: str, *args: TagObject) -> TagObject | None:
    try:
        m = tn_dot(l, m).v
    except TagException:
        return None
    return tn_call(m, args)

def tn_same(l: TagObject, r: TagObject):
    return bool2tbool(l is r)

tag_null = TagNull()