from typing import Callable, Any

class TagType:
    
    def __init__(self, v: int | float | str | Callable | None = None):
        self.v = v
    
    def set(self, v: int | float | str | None):
        self.v = v
    
    def __add__(self, r: object) -> int | float | str:
        return self.v + r.v
    def __sub__(self, r: object) -> int | float:
        return self.v - r.v
    def __mul__(self, r: object) -> int | float | str:
        return self.v * r.v
    def __div__(self, r: object) -> int | float:
        return self.v / r.v
    
    def __eq__(self, r: object) -> bool:
        return self.v == r.v
    def __gt__(self, r: object) -> bool:
        return self.v > r.v
    def __lt__(self, r: object) -> bool:
        return self.v < r.v
    def __ge__(self, r: object) -> bool:
        return self.v >= r.v
    def __le__(self, r: object) -> bool:
        return self.v <= r.v
    
    def __neg__(self) -> int | float:
        return -self.v
    def __pos__(self) -> int | float:
        return +self.v
    
    def __bool__(self):
        return self.v.__bool__()
    
    def is_num(self):
        return isinstance(self.v, (int, float))

    def is_str(self):
        return isinstance(self.v, str)
    
    def is_callable(self):
        return isinstance(self.v, Callable)
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.v(*args, **kwds)

class TagException(Exception):
    
    def __init__(self, where: str, msg: str):
        self.where = where
        self.msg = msg
        super().__init__(f"In {where}, {msg}")