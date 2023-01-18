import typing
from lark.exceptions import UnexpectedInput
from .tagparser import tagparse
from .tagobj import *
from .tagbuiltin import builtin_export
import textwrap

class TagInterpreter:
    
    def __init__(self) -> None:
        self.tree: dict | None = None
        self.table: dict[str, TagRef] = {}
        self.import_dict(builtin_export)
        
        self.returning = False
    
    def import_dict(self, t: dict[str, TagObject]):
        for k, v in t.items():
            self.table[k] = TagRef(v)
    
    def visit(self, node: dict) -> TagRef:
        r = getattr(self, f'visit_{node["type"].name}')(node) or TagRef(tag_null)
        if isinstance(r, TagObject):
            return TagRef(r)
        return r

    def visit_LITERAL(self, node: dict):
        if isinstance(node["value"], int | float):
            return to_tnum(node["value"])
        return TagStr(node["value"])

    def visit_BINOP(self, node: dict):
        if isinstance(node['right'], str):
            r = node['right']
        else:
            r = self.visit(node["right"]).v
        l = self.visit(node["left"]).v
        match node["op"]:
            case '+':
                if is_num(l):
                    if is_num(r):
                        return tn_add(l, r)
                if is_class(l) and l.has_attr('__add__'):
                    return tn_call(l.get_attr('__add__').v, [r])
            case '-':
                if is_num(l):
                    if is_num(r):
                        return tn_sub(l, r)
                if is_class(l) and l.has_attr('__sub__'):
                    return tn_call(l.get_attr('__sub__').v, [r])
            case '*':
                if is_num(l):
                    if is_num(r):
                        return tn_mul(l, r)
                if is_class(l) and l.has_attr('__mul__'):
                    return tn_call(l.get_attr('__mul__').v, [r])
            case '/':
                if is_num(l):
                    if is_num(r):
                        return tn_div(l, r)
                if is_class(l) and l.has_attr('__div__'):
                    return tn_call(l.get_attr('__div__').v, [r])
            case '==':
                return tn_eq(l, r)
            case '!=':
                return tn_neq(l, r)
            case '>':
                return tn_gt(l, r)
            case '>=':
                return tn_ge(l, r)
            case '<':
                return tn_lt(l, r)
            case '<=':
                return tn_le(l, r)
            case 'and':
                return tn_and(l, r)
            case 'or':
                return tn_or(l, r)
            case '.':
                return tn_dot(l, r)
            case 'is':
                return tn_same(l, r)
        
        raise TagException(f"operation {node['op']}",
                           f"{l.NAME} {node['op']} {r.NAME} is incompatible")
    
    def visit_UNARY(self, node: dict) -> TagObject:
        v, o = self.visit(node["value"]).v, node["op"]
        
        match o:
            case '+':
                return tn_pos(v)
            case '-':
                return tn_neg(v)
            case 'not':
                return tn_not(v)
    
    def visit_REFVAR(self, node: dict):
        name: str = node["name"]
        
        if name in self.table:
            return self.table[name]
        raise TagException("variable name", f"No '{name}' found in current context")
    
    def visit_DECLVAR(self, node: dict):
        for name in node["names"]:
            if name in self.table:
                raise TagException("declaration of variable", f"variable '{name}' declared twice")
            self.table[name] = TagRef(tag_null)
    
    def visit_ASSIGN(self, node: dict):
        target = self.visit(node["target"])
        value = self.visit(node["value"])
        
        target.v = value.v
        return target
    
    def visit_DOSTMT(self, node: dict):
        r = tag_null
        for n in node['block']:
            r = self.visit(n)
            if self.returning:
                break
        return r
    
    def visit_FNCALL(self, node: dict):
        caller = self.visit(node['caller']).v
        
        args = []
        for arg in node["args"]:
            args.append(self.visit(arg).v)
        
        if isinstance(caller, TagType):
            return caller.new(args)
        
        return tn_call(caller, args)
    
    def visit_IFSTMT(self, node: dict):
        cond = self.visit(node['condition']).v
        if tbool2bool(cond):
            return self.visit(node['body'])
        return self.visit(node['else'])
    
    def visit_RETSTMT(self, node: dict):
        r = self.visit(node['value'])
        self.returning = True
        return r
    
    def visit_FORLOOP(self, node: dict):
        value = self.visit(node['value']).v
        
        if (not is_class(value)) or (not value.has_attr('__iter__')):
            raise TagException("for loop statement", f"{value.NAME} is not iterable")
        
        old_state = None
        if node['name'] in self.table:
            old_state = self.table[node['name']]
        
        value = typing.cast(TagClass, value)
        
        ctx = TagIterContext()
        
        while True:
            i = tn_call(value.get_attr('__iter__').v, [ctx])
            if ctx.is_end:
                break
            self.table[node['name']] = i
            ctx.step += 1
        
        r = self.table[node['name']]
        
        if old_state:
            self.table[node['name']] = old_state
        else:
            del self.table[node['name']]
        
        return r

def parse(text: str):
    try:
        return tagparse(text)
    except UnexpectedInput as e:
        _e = e # don't want it to print the UnexpectedInput exception
    raise TagException(f"line {_e.line}, column {_e.column}", textwrap.indent(_e.get_context(text), "\n    "))

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