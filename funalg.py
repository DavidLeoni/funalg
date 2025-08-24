
from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable
import collections

# -----------------------------
# Special objects
# -----------------------------

T = TypeVar("T")  

class Empty(Generic[T]):
    """Represents an empty object of a given type C"""
    def __repr__(self):
        return "Empty"

# -----------------------------
# Base symbolic expression
# -----------------------------
class Expr:
    __match_args__ = ("verified",)

    """Base symbolic expression."""
    def __init__(self, verified: bool = False):
        self.verified = verified

    def seval(self, env):
        raise NotImplemented("TODO IMPLEMENT ME!")

    def __repr__(self):
        return f"{self.__class__.__name__}(verified={self.verified})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        """ By default, purely syntactic equality between Python data structures 
        """
        if other is None or other.__class__ != self.__class__:
            return False
        return self is other


class ErrIter:

    def __next__(self):
        raise StopIteration()    

class Err(Expr):
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


class V(Expr):
    """Symbolic variabl."""

    __match_args__ = ("name",)

    def __init__(self, name: str):
        super().__init__(verified=False)
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self):
        return self.__repr__() # self.name maybe later

    def __eq__(self, other):
        if other is None or other.__class__ != self.__class__:
            return False
        return self.name == other.name

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

class L(Expr, collections.abc.Sequence[T]):
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
        
        return ret # + (' [verified]' if self.verified else '')

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
    '''     
    def __bool__(self):
        return self.head is None
    '''
    def seval(self, env):
        h = self.head.seval() if self.head else None
        t = self.tail.seval() if self.tail else None
        return L(h,t)

EL = L()


def tail(lst: L) -> L:
    match lst:
        #case L():   # can't use it because of weird Python __match_args__ rules
        case       []:  return Err()    # ok because our L is also a collection.abc.Sequence
        case [x, *xs]:  return L(xs)

#def subst(old_vars : L[Var], new_vars : L[Var], expr : Expr) -> Expr:


class Return(Expr):

    __match_args__ = ("expr",)

    def __init__(self, expr: Expr):
        self.expr = expr

    def seval(self):
        ret = self.expr.seval()
        return ret

class Call(Expr):

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


class Case(Expr):

    __match_args__ = ("pattern", "body")

    def __init__(self, pattern : Call, body : Expr):
        self.pattern = pattern
        self.body = body


class Match(Expr):

    __match_args__ = ("pattern", "cases")

    def __init__(self, pattern : Call, *cases : Case):
        self.pattern = pattern
        self.cases = list(cases)

class FunDef(Expr):

    __match_args__ = ("name", "args", "body")

    def __init__(self, name: str, args : L, body):
        self.name = name
        self.args = args
        self.body = body 

    def seval(self):
        return self


Tail = FunDef(  "tail", 
                L(V("lst")), 
                Match(V("lst"), 
                    Case(   EL, 
                            Return(Err)),

                    Case(   L(V("x"), V("xs")), 
                            Return(V("xs")))
                    )
)

def seval(expr : Expr):
    return expr.seval()

#class FunCall(Expr):

class Tokens:
    varc = 0

    def fresh_var() -> L:
        Axioms.varc += 1
        name = f"x{Axioms.varc}"
        return V(name)




class BinOp(Expr):

    def __init__(self, a,b):
        self.a = a
        self.b = b        

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a},{self.b})"

class Eq(BinOp):
    pass

class And(BinOp):
    pass

class Or(BinOp):
    pass

class Not(BinOp):
    pass



class Axioms:
    """ Holds all axioms
    """
    def ideq(lhs : Expr, rhs : Expr):
        assert lhs == rhs
        return Eq(lhs, rhs, verified=True)

    def andax(ea : Expr, eb : Expr ):
        assert ea.verified
        assert eb.verified
        return And(ea, eb, verified=True)

    def orax(ea : Expr, eb : Expr ):
        assert ea.verified or eb.verified
        return Or(ea, eb, verified=True)

    def notax(expr : Expr):
        assert expr.verified and not expr
        return Not(expr, verified=True)


def magic(func):
    """ Experimental decorator for theorems, currently does nothing. In thoery, it could:

    - automatically add return commands in match stataments
    - automatically add "if x1 == x2" checks 

    """
    def wrapper():
        func()
    return wrapper

class Theorems:
    """ Holds all theorems
    """

    def ideq_comm(a, b):
        """ a==b -> b==a """
        assert ideq(a,b)
        return ideq(b,a)


    def and_comm(e):
        match e:
            case And(a,b): return andax(b,a)

    def and_t(e):
        return andax(e, True)     

    def or_f(e):
        return orax(e, False)

    def eqtrans_v1(a : Expr, b : Expr, c : Expr):
        ideq(a, b) and ideq(b, c)
        return ideq(a, c)

    def eqtrans_v2(eq1 : Eq, eq2 : Eq):
        match eq1, eq2: 
            case Eq(a,b1, verified=True), Eq(b2,c, verified=True) if b1 == b2:  return ideq(eq1, eq2)
            case _ : assert False

    @magic
    def eqtrans_v3(eq1 : Eq, eq2 : Eq):
        """ would like very much to write just 'b' without numbers but Python throws a SyntaxError
            missing stuff would be fixed by @magic decorator 
        """
        match eq1, eq2: 
            case Eq(a,b1, True),  Eq(b2,c, v=True) : Eq(a, c, True)
            case _                                 : assert False


"""
    def tail_eadd(expr : Expr):
        match expr:
            case  [head]:
"""