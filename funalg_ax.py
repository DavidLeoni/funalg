""" Holds all axioms
"""

from typing import TypeVar, Generic, List, Union, Any, Iterable
from collections.abc import Callable 
import collections
from funalg import *
import copy

def ideq(a : Expr, b : Expr):
    """ Syntactical equality => Equality """
    assert a == b
    return Eq(a, b, cert=True)

def verify(goal, cases, ex):

    for k,v in cases:
        assert goal(k) == v

    assert are_exhaustive(cases.keys(), type(ex))
    ret = goal(ex)
    ret.cert = True
    return ret  


def trutheq(a, b):
    """ verified(a) and verified(b) => verified(a == b) """

    assert verified(a)
    assert verified(b)
    return Eq(a,b, cert=True)

def eq_comm(eq : Eq):
    """ verified(eq) => eq.b == eq.a """

    assert verified(eq)
    return Eq(eq.b, eq.a, cert=True)

def not_false_ax(e : Bool): # let's be strict for now
    assert falsified(e)
    return Not(e, cert=True)    # let's be strict for now

def not_true_ax(e : Bool):
    assert verified(e)   # verified implies True, no need for also  'assert e'
    return Eq(Not(e), False, cert=True)

def andax(a : Bool, b : Bool ):
    assert verified(a)
    assert verified(b)
    return And(a, b, cert=True)

def orax(a : Bool, b : Bool ):
    assert verified(a) or verified(b)
    return Or(a, b, cert=True)


def subst_eq(eq : Eq, p : UniOp):
    """ 
        a == b and p(a)   =>  p(b)

        If a property is verified using eq.a, than it must be verified also when using eq.b
    """
    assert verified(eq)
    assert verified(p(eq.a))
    ret = p(eq.b)
    ret.cert = True  # TODO not very functional
    return ret

def bycases_v0(p: UniOp[Bool], t : type):
    """ p(a) is verified,  p(b) is verified,  T = {a, b}  =>  forall x, p(x:T) is satisfied   

    True : Eq(Not(Not(True)),  True,  cert=True)
    False: Eq(Not(Not(False)), False, cert=True)
    
    Eq(Not(Not(x)), x, cert=True)

    """
    
    literals = enumerate_finite_type(t)
    
    for x in literals:
        assert verified(p(x))

def __certify(e : CExpr, cert : bool):
    """ ONLY to be used in axioms !!!!"""
    c = copy.deepcopy(e)   # TODO actually just copy would be enough as everything should be immutable, 
                           # but just in case...
    c.cert = cert
    return c

def bycases_v1(  goal : CExpr[Bool],   # should contain v 
                    v : V[T], 
                cases : dict[T, CExpr[Bool]]):
    
    """ 
    
    T = {a, b}, cases[a] is verified,  cases[b] is verified  =>  goal is verified   

    Example - given:
    - goal:  Eq(Not(Not(V(x, t))), V(x, t))    either as ast or function
    - v: V(x,t) 
    - cases:
        True : Eq(Not(Not(True)),  True,  cert=True)
        False: Eq(Not(Not(False)), False, cert=True)

    Expect: Eq(Not(Not(V(x, t))), V(x, t), cert=True)

    """
    
    literals = enumerate_finite_type(v.type)

    cgoal = __certify(goal)

    for lit in literals:
        subgoal = cases[lit]
        assert verified(subgoal)
        assert subgoal == subst(v, lit, cgoal) 

    return cgoal


def bycases_v2(goal : Callable[[T], Bool],  # function with no matches 
               cases : dict[T, CExpr[Bool]]):
    """ Possible version with function
    """