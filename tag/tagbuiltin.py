from random import randint
from .tagobj import *
from typing import cast

def rand(args: list[TagObject]):
    if len(args) != 2:
        raise TagException("rand function", f"required exact 2 arguments. Got {len(args)}")
    a, b = args
    if is_num(a) and is_num(b):
        return to_tnum(randint(tn_getv(a), tn_getv(b)))
    raise TagException("rand function", "both argument must be number")

class TagArray(TagClass):
    NAME = "Array"
    
    def __init__(self, arr: list[TagObject] | None = None) -> None:
        super().__init__()
        self.array: list[TagObject] = arr or []
        self.fields['get'] = TagRef(to_func(self.get))
        self.fields['set'] = TagRef(to_func(self.set))
        self.fields['push'] = TagRef(to_func(self.push))
        self.fields['__add__'] = TagRef(to_func(self.__add__))
        self.fields['__init__'] = TagRef(to_func(self._init_))
        self.fields['__iter__'] = TagRef(to_func(self.__iter__))
    
    def _init_(self, args: list[TagObject]):
        self.array = args
        return tag_null
    
    def __add__(self, args: list[TagObject]) -> TagObject:
        if len(args) != 1:
            raise TagException("Array.__add__ method", f"required exact 1 arguments. Got {len(args)}")
        return TagArray(self.array + args[0].array)
    
    def get(self, args: list[TagObject]) -> TagObject:
        if len(args) != 1:
            raise TagException("Array.get method", f"required exact 1 arguments. Got {len(args)}")
        index = args[0]
        if isinstance(index, TagInt):
            try:
                return self.array[index.value]
            except IndexError:
                return tag_null
        raise TagException("Array.get method", f"index argument must be integer not {index.NAME}")
    
    def set(self, args: list[TagObject]) -> TagObject:
        if len(args) != 2:
            raise TagException("Array.set method", f"required exact 2 arguments. Got {len(args)}")
        index, val = args
        if isinstance(index, TagInt):
            try:
                self.array[index.value] = val
            except IndexError:
                raise TagException("Array.set method", "Out of bound")
        raise TagException("Array.set method", f"index argument must be integer not {index.NAME}")
    
    def push(self, args: list[TagObject]) -> TagObject:
        if len(args) != 1:
            raise TagException("Array.push method", f"required exact 1 arguments. Got {len(args)}")
        self.array.append(args[0])
    
    def __iter__(self, args: list[TagObject]):
        if len(args) != 1:
            raise TagException("Array.__iter__", "Required exact 1 argument")
        ctx = args[0]
        if isinstance(ctx, TagIterContext):
            if ctx.step >= len(self.array):
                ctx.is_end = True
                return tag_null
            return self.array[ctx.step]
        raise TagException("Array.__iter__", f"first argument must be IterationContext not {ctx.NAME}")
    
    def len(self, args: list[TagObject]):
        return TagInt(len(self.array))
    
    def repr(self) -> str:
        return '[' + ','.join([tn_repr(x) for x in self.array]) + ']'

class TagTable(TagClass):
    NAME = "Table"
    
    def __init__(self) -> None:
        super().__init__()
        self.table: dict[str, TagObject] = {}
        self.fields['get'] = TagRef(to_func(self.get))
        self.fields['set'] = TagRef(to_func(self.set))
    
    def get(self, args: list[TagObject]) -> TagObject:
        if len(args) != 1:
            raise TagException("Table.get method", f"required exact 1 arguments. Got {len(args)}")
        key = args[0]
        if is_str(key):
            return self.table.get(key.value, tag_null)
        raise TagException("Table.get method", f"key argument must be string not {key.NAME}")
    
    def set(self, args: list[TagObject]) -> TagObject:
        if len(args) != 2:
            raise TagException("Table.set method", f"required exact 2 arguments. Got {len(args)}")
        key, val = args
        if is_str(key):
            self.table[key.value] = val
            return
        raise TagException("Table.set method", f"key argument must be string not {key.NAME}")

class TagIntType(TagType):
    NAME = "integer"
    
    def __init__(self) -> None:
        super().__init__(TagInt)
    
    def new(self, args: list[TagObject]) -> TagInt:
        c: TagInt = self.tclass()
        if len(args) != 1:
            c.value = 0
        else:
            v = args[0]
            if is_num(v) or is_str(v):
                try:
                    c.value = int(v.value)
                except ValueError:
                    raise TagException('integer.__init__', "cannot parse string to number")
            elif is_class(v) and v.has_str('__int__'):
                r = tn_call(v.get_attr('__int__').v)
                if not is_num(r):
                    raise TagException(f'{v.NAME}.__int__', f"must return integer not {r.NAME}")
                c.value = r.value
            else:
                raise TagException(f'integer.__init__', f'Cannot convert {v.NAME} to integer')
        return c

class TagFloatType(TagType):
    NAME = "float"
    
    def __init__(self) -> None:
        super().__init__(TagInt)
    
    def new(self, args: list[TagObject]) -> TagInt:
        c: TagInt = self.tclass()
        if len(args) != 1:
            c.value = 0
        else:
            v = args[0]
            if is_num(v) or is_str(v):
                try:
                    c.value = float(v.value)
                except ValueError:
                    raise TagException('float.__init__', "cannot parse string to float")
            elif is_class(v) and v.has_str('__float__'):
                r = tn_call(v.get_attr('__float__').v)
                if not is_num(r):
                    raise TagException(f'{v.NAME}.__float__', f"must return float not {r.NAME}")
                c.value = r.value
            else:
                raise TagException(f'float.__float__', f'Cannot convert {v.NAME} to float')
        return c

class TagNativeFunc(TagType):
    NAME = "NativeFunc"
    
    def __init__(self) -> None:
        super().__init__(TagNativeFunc)
    
    def new(self, args: list[TagObject]) -> TagClass:
        raise TagException(f"NativeFunc.__init__", f"NativeFunc is for comparing only. not creating")

tag_int_type = TagIntType()
tag_float_type = TagFloatType()
tag_native_type = TagNativeFunc()

def get_type(args: list[TagObject]) -> TagType:
    if len(args) != 1:
        raise TagException("type function", "required exact 1 argument")
    if isinstance(args[0], TagType | TagNull):
        return args[0]
    if isinstance(args[0], TagInt):
        return tag_int_type
    if isinstance(args[0], TagFloat):
        return tag_float_type
    if isinstance(args[0], TagNativeFunc):
        return tag_native_type
    if isinstance(args[0], TagClass):
        if args[0].TYPE is None:
            raise ValueError(f"{args[0].NAME} doesn't have type defined")
        return args[0].TYPE
    raise NotImplementedError(f"{args[0].__class__.__name__}")

builtin_export: dict[str, TagObject] = {
    "rand": to_func(rand),
    "true": TagInt(1),
    "false": TagInt(0),
    "null": tag_null,
    "Array": TagType(TagArray),
    "Table": TagType(TagTable),
    "str": TagType(TagStr),
    "int": tag_int_type,
    "float": tag_float_type,
    "NativeFunc": tag_native_type,
    "type": to_func(get_type)
}