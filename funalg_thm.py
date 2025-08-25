""" Holds all theorems
"""

from funalg import *
from funalg_ax import *

from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable
import collections




def ideq_comm_v1(a, b):
    """ a==b -> b==a """

    assert ideq(a,b)
    return ideq(b,a)

def ideq_comm_v2(e : Eq):
    """ a==b -> b==a """

    assert ideq(e.a,e.b)
    return ideq(e.b,e.a)

def ideq_comm_v3(e : Eq):
    """ a==b -> b==a """
    return ideq(e.b,e.a)


def and_comm(e : And):
    match e:
        case And(a,b):  return andax(b,a)
        case        _:  assert False
    
def and_t(e : And):
    return andax(e, True)     

def or_f(e : Or):
    return orax(e, False)


def not_not_case_true(ex : Not[Not[True]]):
    """ not(not(True)) == True """

    e = ex.e.e

    eq   = not_true_ax(e)    # produces a certified  not(True) == False
    sweq = eq_comm(eq)     # produces a certified  False == not(True)   
    notnott = subst_eq(sweq, not_false_ax)  # applies not_false_ax to not(True) to get a certified not(not(True))
    # goal: Not(Not(True)) == True
    return trutheq(notnott, True)

def not_not_case_false(ex : Not[Not[False]]):
    """ not(not(False)) == False """

    e = ex.e.e

    v = not_false_ax(e)   # produces a certified Not(False)  (which is True)
    return not_true_ax(v) # produces a certified  Not(Not(False)) == False  


def not_not(ex : Not[Not[Bool]]) -> Eq: # let's have strictly boolean types for now
    """ not(not(e)) == e """

    e = ex.e.e
    
    match e:
        case True : return not_not_case_true(ex)
        case False: return not_not_case_false(ex)
        case _: assert False   # just in case

def eqtrans_v1(a : Expr, b : Expr, c : Expr):
    ideq(a, b) and ideq(b, c)
    return ideq(a, c)

def eqtrans_v2(eq1 : Eq, eq2 : Eq):
    match eq1, eq2: 
        case Eq(a,b1, certificate=True), Eq(b2,c, certificate=True) if b1 == b2:  return ideq(eq1, eq2)
        case _ : assert False

@magic
def eqtrans_v3(eq1 : Eq, eq2 : Eq):
    """ would like very much to write just 'b' without numbers but Python throws a SyntaxError
        missing stuff would be fixed by @magic decorator 
    """
    match eq1, eq2: 
        case Eq(a,b1, True),  Eq(b2,c, v=True) : Eq(a, c, True)
        case _                                 : assert False
