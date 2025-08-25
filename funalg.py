
debug_show_cert = False

from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable, TypeVarTuple
from typing import Self
import collections

from typing import Literal, Union, get_args, get_origin
from types import UnionType
from enum import Enum
import itertools

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
    __match_args__ = ("cert",)

    """Base symbolic expression."""
    def __init__(self, cert: bool = None):
        self.cert = cert

    def seval(self, env) -> Self:
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

    def certis(self) -> str: 
        return f"cert={self.cert}" if debug_show_cert and certified(self) else ""
        
    def walk(self) -> list[Self]:
        return []        


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

def get_cert(obj) -> bool | None:
    """ A certified object has been proved to eventually evaluate to exactly True or False """
    if type(obj) is bool:
        return obj
    elif isinstance(obj, CExpr):
        return obj.cert
    else:
        return None

def certified(obj) -> bool:
    """ A certified object has been proved to eventually evaluate to exactly True or False """
    if type(obj) is bool:
        return True
    elif isinstance(obj, CExpr):
        return obj.cert is not None
    else:
        return False


def verified(obj) -> bool:
    """ A verified object has been proved to eventually evaluate to exactly True """
    return obj is True or (isinstance(obj, CExpr) and obj.cert is True)

def falsified(obj) -> bool:
    """ A falsified object has been proved to eventually evaluate to exactly False """
    return obj is False or (isinstance(obj, CExpr) and obj.cert is False)


#type EBool = Expr[Bool]  # ?


class EBool(CExpr):  
    """ TODO Experimental type, probably redundant
    """

    def __init__(self, name : str, tf : bool, cert : bool = None):
        super().__init__(cert=cert)

        self.name = name
        self.tf = tf
        

    def __bool__(self):
        return self.tf

    def __repr__(self):
        return self.name 

    def __eq__(self, other):
        if type(other) is bool:
            return self.tf is other
        elif type(other) is EBool:
            return self is other
        else:
            return False

TRUE = EBool('TRUE', True, cert=True)
FALSE = EBool('FALSE', False, cert=False)


class V(CExpr[T]):
    """ Symbolic variable """

    __match_args__ = ("name",)

    def __init__(self, name: str, t: type = None, cert:bool = None):
        super().__init__(cert)
        self.name = name
        self.type = t

    def __repr__(self):
        args = ''
        st = f",{self.type.__name__}" if self.type else '' 
        cert = self.certis()
        certi = ',' + cert if cert else ''
        return f"{self.__class__.__name__}({repr(self.name)}{st}{certi})"

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
        
        return ret # + (' [cert]' if self.cert else '')

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


    def walk(self) -> list[CExpr]:
        return list(self)

EL = L()



class BinOp(CExpr[T]): 
    """ To keep things simple,  T is for both inputs and output type """

    def __init__(self,a : T, b : U, cert=False):
        super().__init__(cert=cert)
        self.a = a
        self.b = b        

    def __repr__(self):
        c = f', {self.certis()}'
        return f"{self.__class__.__name__}({self.a}, {self.b}{c})"

    def walk(self) -> list[CExpr]:
        return [self.a, self.b]


class UniOp(CExpr[T]): 
    """ To keep things simple, T is both input and output type """

    def __init__(self, e, cert=False):
        super().__init__(cert=cert)
        self.e = e

    def __repr__(self):
        c = f', {self.certis()}'
        return f"{self.__class__.__name__}({self.e}{c})"

    def walk(self) -> list[CExpr]:
        return [self.e]

class Return(UniOp[T]):

    __match_args__ = ("expr",)

    def __init__(self, expr: Expr):
        self.expr = expr

    def seval(self):
        ret = self.expr.seval()
        return ret

class Fun(Generic[*Ts, T], CExpr[[*Ts,T]]):
    """ adding Generic[*Ts, T] because Python 3.12.3 is dumb
    """

    __match_args__ = ("args", "body")

    def __init__(self, args : [*Ts], body : CExpr[T]):
        self.args = args
        self.body = body 

    def seval(self, env):
        return self

    def walk(self) -> list[CExpr]:
        return [self.args, self.body]

class Def(CExpr[T]):   
    """ Represents an assignment, sounds better than Ass  O_o'
        - since everything is immutable there's no (shouldn't) be double defs)
        - Let's just have var type and expression coincide for now ....
    """

    __match_args__ = ("v", "e")

    def __init__(self, v : V[T], e : T):
        self.v = v
        self.e = e 

    def seval(self, env):
        #return [v:] + env
        raise Exception("TODO IMPLEMENT ME!")

    def walk(self) -> list[CExpr]:
        return [self.v, self.e]


class FunDef(Generic[*Ts, T], Def[Fun[*Ts, T]]):  # adding Generic[*Ts, T] because Python 3.12.3 is dumb
    """ adding Generic[*Ts, T] because Python 3.12.3 is dumb
    """
    pass


class Call(CExpr):

    __match_args__ = ("funv", "args")

    def __init__(funv: V[Fun], args: L):
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

    def walk(self) -> list[CExpr]:
        return [self.funv, self.args]


class Case(CExpr):

    __match_args__ = ("pattern", "body")

    def __init__(self, pattern : Call, body : CExpr):
        self.pattern = pattern
        self.body = body

    def walk(self) -> list[CExpr]:
        return [self.pattern, self.body]


class Match(CExpr):

    __match_args__ = ("pattern", "cases")

    def __init__(self, pattern : Call, *cases : Case):
        self.pattern = pattern
        self.cases = list(cases)

    def walk(self) -> list[CExpr]:
        return [self.pattern, self.cases]



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
    def __init__(self, e, cert=None):
        
        if certified(e):
            if cert is not None and cert is e:
                raise ValueError(f"Inconsistent cert value while creating Not({e}, cert={cert})")
            self.cert = not get_cert(e)
        else:
            self.cert = cert

        self.e = e
        
    def seval(self, env):
        return not self.e.seval(env)

class Eq(BinOp):
    pass

        
def subst(old_var : V[T], new_var : V[T], expr : Expr) -> Expr:
    raise Exception("TODO IMPLEMENT ME!")

def substs(old_vars : L[V], new_vars : L[V], expr : Expr) -> Expr:
    raise Exception("TODO IMPLEMENT ME!")

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


def enumerate_finite_type(tp : type) -> list[type]:
    """Return all possible values for a *finite* type annotation.
    
        TODO incomplete, probably buggy
    """

    origin = get_origin(tp)
    args = get_args(tp)

    # Handle Literal types
    if origin is Literal:
        return list(args)

    # Handle Enums
    if isinstance(tp, type) and issubclass(tp, Enum):
        return list(tp)

    # Handle bool explicitly
    if tp is bool:
        return [True, False]

    # Handle NoneType
    if tp is type(None):
        return [None]

    # Handle Unions
    if origin is Union or origin is UnionType:
        results = []
        for arg in args:
            results.extend(enumerate_finite_type(arg))
        return results

    # Handle tuples of finite types
    if origin is tuple or origin is Tuple:
        sublists = [enumerate_finite_type(arg) for arg in args]
        return [tuple(comb) for comb in itertools.product(*sublists)]

    # Could extend with ranges, TypedDict, etc.
    raise TypeError(f"Don't know how to enumerate {tp}")


