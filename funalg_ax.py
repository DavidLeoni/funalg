""" Holds all axioms
"""

from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable
import collections
from funalg import *


def ideq(lhs : Expr, rhs : Expr):
    """ Syntactical equality """
    assert lhs == rhs
    return Eq(lhs, rhs, verified=True)


def trutheq(a, b):
    assert verified(a)
    assert verified(b)
    return Eq(a,b, verified=True)

def andax(a : Bool, b : Bool ):
    assert verified(a)
    assert verified(b)
    return And(a, b, verified=True)

def orax(a : Bool, b : Bool ):
    assert verified(a) or verified(b)
    return Or(a, b, verified=True)

def not_false_ax(e : Bool): # let's be strict for now
    assert not e
    return Not(e, verified=True)    # let's be strict for now

def not_true_ax(e : Bool):
    assert verified(e)   # verified implies True, no need for also  'assert e'
    return Eq(Not(e), False, verified=True)

def subst_eq(e : Eq, p : UniOp):
    """ if a property is satisfied using lhs of e, than it must be satisfied also when using rhs"""

    assert verified(p(e.a))
    ret = p(e.b)
    ret.verified = True  # TODO not very functional
    return ret

def eq_comm(e : Eq):
    assert verified(e)
    return Eq(e.b, e.a, verified=True)
