#!/bin/python3

from operator import add, sub, mul, and_, or_, truediv
from functools import reduce
from itertools import islice
from math import sqrt

BLANKS = ' \n\r\t\v'
DELIMS = {
    '(': ')',
    '[': ']',
    '{': '}',
}

BUILTINS = {
    '+':     lambda Γ, *args: reduce(add, (lisp_eval1(arg, Γ) for arg in args)),
    '-':     lambda Γ, *args: reduce(sub, (lisp_eval1(arg, Γ) for arg in args)),
    '×':     lambda Γ, *args: reduce(mul, (lisp_eval1(arg, Γ) for arg in args)),
    '/':     lambda Γ, *args: reduce(truediv, (lisp_eval1(arg, Γ) for arg in args)),
    '¬':     lambda Γ, arg: not lisp_eval1(arg, Γ),
    '∧':     lambda Γ, *args: reduce(and_, (lisp_eval1(arg, Γ) for arg in args)),
    '∨':     lambda Γ, *args: reduce(or_, (lisp_eval1(arg, Γ) for arg in args)),
    '=':     lambda Γ, *args: all(l == r for l, r in sliding_window(lisp_eval1(arg, Γ) for arg in args)),
    '≠':     lambda Γ, *args: all(l != r for l, r in sliding_window(lisp_eval1(arg, Γ) for arg in args)),
    '<':     lambda Γ, *args: all(l < r for l, r in sliding_window(lisp_eval1(arg, Γ) for arg in args)),
    '>':     lambda Γ, *args: all(l > r for l, r in sliding_window(lisp_eval1(arg, Γ) for arg in args)),
    '≤':     lambda Γ, *args: all(l <= r for l, r in sliding_window(lisp_eval1(arg, Γ) for arg in args)),
    '≥':     lambda Γ, *args: all(l >= r for l, r in sliding_window(lisp_eval1(arg, Γ) for arg in args)),
    '√':     lambda Γ, n: sqrt(lisp_eval1(n, Γ)),
    'print': lambda Γ, *args: print(*(lisp_eval1(arg, Γ) for arg in args)),
    'cond':  lambda Γ, *args: next((lisp_eval(r, Γ) for l, *r in args if lisp_eval1(l, Γ)), []),
    'let':   lambda Γ, name, expr: Γ.update({name: lisp_eval1(expr, Γ)}),
    'list':  lambda Γ, *args: [lisp_eval1(arg, Γ) for arg in args],
    'plan':  lambda Γ, *args: Plan(args),
    'true':  True,
    'false': False,
    'nil':   []
}

# "Go to (100, 200), and then go to the kitchen"
SRC = """
{plan
    {objects
        [the-kitchen nil]}
    [steps
        {GOTO
            [active True]
            [where  [100 200]]
            [post   (∧ (near? [100 200]) (< V 0.01))]}
        {GOTO
            [active False]
            [where  nil]
            [pre    (near? [100 200])]
            [post   (∧ (inside? the-kitchen) (< V 0.01))]}]}
"""


class Step:
    def __init__(self, L):
        self.type = L[0]
        self.active = False
        self.attrs = {}

        for item in L[1:]:
            if item[0] == 'active':
                self.type = not not item[1]
            else:
                k, v = item
                self.attrs[k] = v

    def __repr__(self):
        return f'Step {self.__dict__}'

class Plan:
    def __init__(self, L):
        self.objects   = {}
        self.relations = []
        self.steps     = []

        for item in L:
            if item[0] == 'objects':
                self.objects = {k: v for k, v in item[1:]}
            elif item[0] == 'relations':
                self.relations = item[1:]
            elif item[0] == 'steps':
                self.steps = [Step(step) for step in item[1:]]
            else:
                raise Exception(f'invalid attribute {item[0]} for Plan')

    def __repr__(self):
        return f'Plan {self.__dict__}'

def sliding_window(L, n=2):
    result = tuple(islice(L, n))
    if len(result) == n:
        yield result
    for elem in L:
        result = result[1:] + (elem,)
        yield result

def parse_atom(src):
    match = ''

    while src:
        head, *tail = src
        if head in {*BLANKS, *DELIMS, *DELIMS.values()}:
            break
        match += head
        src = tail

    try:
        match = int(match)
    except ValueError:
        pass

    return match, src

def parse(src, delim=None):
    L = []
    val = None

    while src:
        head, *tail = src

        if head in BLANKS:
            src = tail
            continue
        elif head in DELIMS:
            val, tail = parse(tail, DELIMS[head])
        elif head == delim:
            return L, tail
        elif head in DELIMS.values():
            raise Exception(f"mismatched delimiters (expected '{delim}', got '{head}')")
        else:
            val, tail = parse_atom(src)

        L.append(val)
        src = tail

    if delim:
        raise Exception(f"unexpected EOF (expected '{delim}')")

    return L, val

def lisp_eval1(expr, Γ):
    if expr == []:
        return []
    elif type(expr) in {Plan, int, float, bool}:
        return expr
    elif type(expr) is list:
        f, *args = expr
        f = lisp_eval1(f, Γ)
        value = f(Γ, *args)
        return [] if value == None else value
    elif expr in Γ:
        return Γ[expr]
    else:
        raise Exception(f"undefined '{expr}'")

def lisp_eval(L, Γ=None):
    # initialize context if not provided
    if not Γ:
        Γ = BUILTINS.copy()

    return [lisp_eval1(elem, Γ) for elem in L]

L, _ = parse(SRC)
print(L)
Γ = BUILTINS.copy()
L = lisp_eval(L)
print(L)
print(L[0])
print({k: v for k, v in Γ.items() if k not in BUILTINS})