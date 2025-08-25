""" Holds all axioms
"""

from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable
import collections
from funalg import *


def ideq(a : Expr, b : Expr):
    """ Syntactical equality => Equality """
    assert a == b
    return Eq(a, b, certificate=True)

def trutheq(a, b):
    """ verified(a) and verified(b) => verified(a == b) """

    assert verified(a)
    assert verified(b)
    return Eq(a,b, certificate=True)

def eq_comm(eq : Eq):
    """ verified(eq) => eq.b == eq.a """

    assert verified(eq)
    return Eq(eq.b, eq.a, certificate=True)

def not_false_ax(e : Bool): # let's be strict for now
    assert falsified(e)
    return Not(e, certificate=True)    # let's be strict for now

def not_true_ax(e : Bool):
    assert verified(e)   # verified implies True, no need for also  'assert e'
    return Eq(Not(e), False, certificate=True)

def andax(a : Bool, b : Bool ):
    assert verified(a)
    assert verified(b)
    return And(a, b, certificate=True)

def orax(a : Bool, b : Bool ):
    assert verified(a) or verified(b)
    return Or(a, b, certificate=True)


def subst_eq(eq : Eq, p : UniOp):
    """ 
        a == b and p(a)   =>  p(b)

        If a property is satisfied using eq.a, than it must be satisfied also when using eq.b
    """
    assert verified(eq)
    assert verified(p(eq.a))
    ret = p(eq.b)
    ret.certificate = True  # TODO not very functional
    return ret

