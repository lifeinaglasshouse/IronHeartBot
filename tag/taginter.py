from lark.exceptions import UnexpectedInput
from .tagparser import tagparse
from .tagobj import TagType, TagException
from .tagbuiltin import builtin_export
import textwrap

class TagInterpreter:
    
    def __init__(self) -> None:
        self.tree: dict | None = None
        self.table: dict[str, TagType] = {}
        
        for k, v in builtin_export.items():
            self.table[k] = v
        
        self.returning = False
    
    def visit(self, node: dict) -> TagType:
        return getattr(self, f'visit_{node["type"].name}')(node)

    def visit_LITERAL(self, node: dict):
        return TagType(node["value"])

    def visit_BINOP(self, node: dict):
        l, r = self.visit(node["left"]), self.visit(node["right"])
        match node["op"]:
            case '+':
                if l.is_num():
                    if r.is_num():
                        return l + r
                if l.is_str():
                    if r.is_str():
                        return l + r
            case '-':
                if l.is_num():
                    if r.is_num():
                        return l - r
            case '*':
                if l.is_num():
                    if r.is_num():
                        return l * r
                if l.is_str():
                    if isinstance(r, int):
                        return l * r
            case '/':
                if l.is_num():
                    if r.is_num():
                        if r == 0:
                            raise TagException("operation [/]", "Cannot divide by zero")
                        return l / r
            case '==':
                return l == r
            case '!=':
                return l != r
            case '>':
                return l > r
            case '>=':
                return l >= r
            case '<':
                return l < r
            case '<=':
                return l <= r
            case 'and':
                return int(l and r)
            case 'or':
                return int(l or r)
        
        raise TagException(f"operation [{node['op']}]",
                           f"{type(l).__name__} and {type(r).__name__} is incompatible")
    
    def visit_UNARY(self, node: dict):
        v, o = self.visit(node["value"]), node["op"]
        
        match o:
            case '+':
                if v.is_num():
                    return +v
            case '-':
                if v.is_num():
                    return -v
            case 'not':
                return int(not v)
        
        raise TagException(f"unary [{o}]", f"{o}{v} is invalid")
    
    def visit_REFVAR(self, node: dict):
        name: str = node["name"]
        
        if name in self.table:
            return self.table[name]
        raise TagException("variable name", f"No '{name}' found in current context")
    
    def visit_DECLVAR(self, node: dict):
        for name in node["names"]:
            if name in self.table:
                raise TagException("declaration of variable", f"variable '{name}' declared twice")
            self.table[name] = TagType()
    
    def visit_ASSIGN(self, node: dict):
        target = self.visit(node["target"])
        value = self.visit(node["value"])
        
        target.set(value.v)
        return target
    
    def visit_DOSTMT(self, node: dict):
        r = TagType()
        for n in node['block']:
            r = self.visit(n)
            if self.returning:
                break
        return r
    
    def visit_FNCALL(self, node: dict):
        caller = self.visit(node['caller'])
        
        if not caller.is_callable():
            raise TagException(f"operation call", f"{type(caller)} is not callable")
        
        args = []
        for arg in node["args"]:
            args.append(self.visit(arg))
        
        return caller(*args)
    
    def visit_IFSTMT(self, node: dict):
        cond = self.visit(node['condition'])
        if cond:
            return self.visit(node['body'])
        return self.visit(node['else'])
    
    def visit_RETSTMT(self, node: dict):
        r = self.visit(node['value'])
        self.returning = True
        return r

def interpret(text: str):
    i = TagInterpreter()
    _e = None
    try:
        r = tagparse(text)
        v = i.visit(r)
        return v, i
    except UnexpectedInput as e:
        _e = e # don't want it to print the UnexpectedInput exception
    raise TagException(f"line {_e.line}, column {_e.column}", textwrap.indent(_e.get_context(text), "\n    "))