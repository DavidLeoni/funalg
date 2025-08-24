
debug_show_certified = False

from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable, TypeVarTuple
import collections

# -----------------------------
# Special objects
# -----------------------------

T = TypeVar("T")  
U = TypeVar("U")
Ts = TypeVarTuple("Ts")

type Bool = True | False

class Empty(Generic[T]):
    """Represents an empty object of a given type C"""
    def __repr__(self):
        return "Empty"

# -----------------------------
# Base symbolic expression
# -----------------------------
class CExpr(Generic[*Ts]):
    __match_args__ = ("certified",)

    """Base symbolic expression."""
    def __init__(self, certified: bool = None):
        self.certified = certified

    def seval(self, env):
        raise NotImplemented("TODO IMPLEMENT ME!")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.certis()})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        """ By default, purely syntactic equality between Python data structures 
        """
        if other is None or other.__class__ != self.__class__:
            return False
        return self.__dict__ == other.__dict__

    def certis(self): 
        return f"certified={certified(self)}" if debug_show_certified and certified(self) is not None else ""
        
type Expr = CExpr | Bool | list | str | tuple

class ErrIter:

    def __next__(self):
        raise StopIteration()    

class Err(CExpr):
    """Represents an error in computation"""
    
    def __init__(self, *args):
        self._funalg_args = list(args)

    def __getattr__(self, name: str):
        return self
    
    def __call__(self, *args, **kwargs):
        return self
    
    def __repr__(self):
        
        msg = ' '.join([repr(arg) for arg in self._funalg_args])
        
        return f"{self.__class__.__name__}({msg})"
    
    def __iter__(self):
        return ErrIter()

    def __next__(self):
        raise StopIteration()

    def __eq__(self, other):
        if other is None or other.__class__ != self.__class__:
            return False
        return self.__class__ is other.__class__  #  so tail(L('a')) == Err() works

def certified(obj):
    """ A certified object has been proved to eventually evaluate to exactly True or False """
    if type(obj) is bool:
        return obj
    elif isinstance(obj, CExpr):
        return obj.certified
    else:
        return None

def verified(obj):
    """ A verified object has been proved to eventually evaluate to exactly True """
    return obj is True or (isinstance(obj, CExpr) and obj.certified is True)

def falsified(obj):
    """ A falsified object has been proved to eventually evaluate to exactly False """
    return obj is False or (isinstance(obj, CExpr) and obj.certified is False)


class V(CExpr):
    """Symbolic variabl."""

    __match_args__ = ("name",)

    def __init__(self, name: str):
        super().__init__(certified=False)
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self):
        return self.__repr__() # self.name maybe later

    def seval(self, env):
        raise Exception(f"Unbounded variable {repr(self)}")


class LIter:

    def __init__(self, lst : "L"):
        self.current = lst

    def __iter__(self):  # not sure we need this 
        return LIter(self.current)

    def __next__(self):
        lst = self.current
        if lst is None or lst.head is None:
            raise StopIteration

        self.current = lst.tail
        return lst.head

EL = None

class L(CExpr, collections.abc.Sequence[T]):
    """Symbolic finite list."""

    __match_args__ = ("head", "tail")

    def __init__(self, head : Expr | list | tuple = None, tail: "L" = None):
        super().__init__(bool(head))

        if type(head) == list or type(head) == tuple:

            if tail is not None:
                raise ValueError(f"Trying to create an {self.__class__.__name__} by passing both sequence and a tail")
            if len(head) == 0:
                self.head = None
                self.tail = None
            else:
                self.head = head[0]
                if len(head) == 1:
                    self.tail = None
                else: 
                    self.tail = L(head[1:])
        else:
            self.head = head
            self.tail = tail

    def __repr__(self):
        if self.head is None:
            ret = 'L()'
        else:
            lst = [f"L({repr(e)}" for e in self]
            ret = ', '.join(lst) + (')' * len(lst))
        
        return ret # + (' [certified]' if self.certified else '')

    def __iter__(self):
        return LIter(self)

    def __add__(self, other: "L") -> "L":
        return L(self.elments + other.elments)

    def __eq__(self, other):
        if other is None or other.__class__ != self.__class__:
            return False
        return self.head == other.head and self.tail == other.tail

    def __len__(self):
        if self.head is None:
            return 0
        rest = len(self.tail) if self.tail else 0
        return 1 + rest


    """ not needed as we're overriding __len__ so Python automatically uses that to check truthiness      
    def __bool__(self):
        return self.head is None
    """

    def __getitem__(self, index):  
        if type(index) != int:
            raise TypeError(f"Wrong index type (expected int): {type(index)}")
        if index < 0:
            raise IndexError(f"Negative indexes are not currently supported, got {index}")
        
        c = 0
        for el in self:
            if c == index:
                return el
            c += 1
        
        raise IndexError(f"Index exceeds list length: {index}")
    
    

    def seval(self, env):
        h = self.head.seval() if self.head else None
        t = self.tail.seval() if self.tail else None
        return L(h,t)

EL = L()



class BinOp(CExpr[T,U]):

    def __init__(self,a : T, b : U, certified=False):
        super().__init__(certified=certified)
        self.a = a
        self.b = b        

    def __repr__(self):
        c = f', {self.certis()}'
        return f"{self.__class__.__name__}({self.a}, {self.b}{c})"
        
class UniOp(CExpr[T]):

    def __init__(self, e, certified=False):
        super().__init__(certified=certified)
        self.e = e

    def __repr__(self):
        c = f', {self.certis()}'
        return f"{self.__class__.__name__}({self.e}{c})"


class Return(UniOp[T]):

    __match_args__ = ("expr",)

    def __init__(self, expr: Expr):
        self.expr = expr

    def seval(self):
        ret = self.expr.seval()
        return ret

class Call(CExpr):

    __match_args__ = ("funv", "args")

    def __init__(funv: V, args: L):
        self.funv = funv
        self.args = args

    def seval(self, env):
        if funv.name not in env:
            return Err(f"No currently defined function named {funv.name}")

        fundef = env[funv.name]

        if len(self.args) != len(fundef.args):
            return Err(f"Mismatching number of arguments! fundef args: {len(fundef.args)} != call {self.args}=")
 
        new_body = fundef.body
        fvs = [Tokens.fresh_var() for i in range(len(self.args))]
            
        for fv in fvs:
            new_body = subst(fundef.args[i], fv, new_body) 

        for i in range(len(self.args)):
            new_body = subst(fvs[i], self.args[i], new_body) 

        ret = new_body.seval(env)
        
        return ret


class Case(CExpr):

    __match_args__ = ("pattern", "body")

    def __init__(self, pattern : Call, body : CExpr):
        self.pattern = pattern
        self.body = body


class Match(CExpr):

    __match_args__ = ("pattern", "cases")

    def __init__(self, pattern : Call, *cases : Case):
        self.pattern = pattern
        self.cases = list(cases)

class FunDef(CExpr):

    __match_args__ = ("name", "args", "body")

    def __init__(self, name: str, args : L, body):
        self.name = name
        self.args = args
        self.body = body 

    def seval(self):
        return self

class Rest(UniOp[T]):
    pass


def seval(expr : CExpr):
    return expr.seval()

#class FunCall(Expr):

class Tokens:
    varc = 0

    def fresh_var() -> L:
        Axioms.varc += 1
        name = f"x{Axioms.varc}"
        return V(name)

###############  Booleans

class And(BinOp):
    pass

class Or(BinOp):
    pass

class Not(UniOp[T]):
    def __init__(self, e, certified=None):
        
        if e is True or e is False:
            if certified is not None and certified is e:
                raise ValueError(f"Inconsistent certified value while creating Not({e}, certified={certified})")
            self.certified = not e
        else:
            self.certified = certified

        self.e = e
        
    def seval(self, env):
        return not self.e.seval(env)

class Eq(BinOp):
    pass


################  Functions

def tail(lst: L) -> L:
    match lst:
        #case L():   # can't use it because of weird Python __match_args__ rules
        case       []:  return Err()    # ok because our L is also a collection.abc.Sequence
        case [x, *xs]:  return L(xs)

Tail = FunDef(  "tail", 
                L(V("lst")), 
                Match(V("lst"), 
                    Case(   EL,
                            Return(Err)),

                    Case(   L(V("x"), Rest(V("xs"))), 
                            Return(V("xs")))
                    )
)


def head(lst: L) -> L:
    match lst:
        case        []: return Err()
        case  [x, *xs]: return x
        

#def subst(old_vars : L[Var], new_vars : L[Var], expr : Expr) -> Expr:


def magic(func):
    """ Experimental decorator for theorems, currently does nothing. In thoery, it could:

    - automatically add return commands in match stataments
    - automatically add "if x1 == x2" checks 

    """
    def wrapper():
        func()
    return wrapper

"""
def tail_eadd(expr : Expr):
    match expr:
        case  [head]:
"""