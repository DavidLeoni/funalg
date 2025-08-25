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


def not_not_true(ex : Not[Not[True]]):
    """ not(not(True)) == True """

    e = ex.e.e

    eq   = not_true_ax(e)    # produces a certified  not(True) == False
    sweq = eq_comm(eq)       # produces a certified  False == not(True)   
    notnott = subst_eq(sweq, not_false_ax)  # applies not_false_ax to not(True) to get a certified not(not(True))
    # goal: Not(Not(True)) == True
    return trutheq(notnott, True)

def not_not_false(ex : Not[Not[False]]):
    """ not(not(False)) == False """

    e = ex.e.e

    v = not_false_ax(e)   # produces a certified Not(False)  (which is True)
    return not_true_ax(v) # produces a certified  Not(Not(False)) == False  


def not_not_v1(ex : Not[Not[Bool]]) -> Eq: # let's have strictly boolean types for now
    """ not(not(e)) == e """

    e = ex.e.e
    
    match e:
        case True : return not_not_true(ex)
        case False: return not_not_false(ex)
        case _: assert False   # just in case

def not_not_v2(ex : Expr) -> Eq:
    """  not(not(ex)) == ex  """

    nnex = Not(Not(ex))
    
    """ when we will have an astifier
    def goalf(e):
        assert not(not(e)) == e
    """

    def goal(x : Expr):
        return Eq(Not(Not(x)), x)   # notice here we *don't* put the certificate

    cases = {
        True : not_not_true(True),
        False: not_not_false(False)
    }
    
    return ret


def not_not_v3(ex : Not[Not[Bool]]) -> Eq: # let's have strictly boolean types for now
    """ not(not(ex)) == ex """

    match ex:
        case Not(Not(True)) : return not_not_true(ex)
        case Not(Not(False)): return not_not_false(ex)
        case _: assert False   # just in case


def not_not_v4(ex : Not[Not[EBool]]) -> Eq: # let's have strictly boolean types for now
    """ not(not(ex)) == ex """

    match ex:
        case Not(Not(True)) : return not_not_true(ex)
        case Not(Not(False)): return not_not_false(ex)
        case _: assert False   # just in case


def not_not_true_v5(ex : Not[Not[Expr]]):
    """ not(not(True)) == True """

    e = ex.e.e

    assert verified(e)

    eq   = not_true_ax(e)    # produces a certified  not(True) == False
    sweq = eq_comm(eq)       # produces a certified  False == not(True)   
    notnott = subst_eq(sweq, not_false_ax)  # applies not_false_ax to not(True) to get a certified not(not(True))
    # goal: Not(Not(True)) == True
    return trutheq(notnott, True)

def not_not_false_v5(ex : Not[Not[Expr]]):
    """ not(not(False)) == False """

    e = ex.e.e

    assert falsified(e)

    v = not_false_ax(e)   # produces a certified Not(False)  (which is True)
    return not_true_ax(v) # produces a certified  Not(Not(False)) == False  


def not_not_v5(ex : Not[Not[CExpr[Bool]]]) -> Eq:
    """ not(not(ex)) == ex """

    match ex:
        case Not(Not(CExpr(cert=True)))  : return not_not_true_v5(ex)
        case Not(Not(CExpr(cert=False))) : return not_not_false_v5(ex)
        case Not(Not(CExpr(cert=None)))  : return "TODO ????"  
        case _ : assert False

def verifier(ex : Not[Not[Bool]]):
    """ given input ex:
    
        - is there a target goal?

        - is there a match stmt?
        
        - is ex finite or recursive?
            - finite:
                - enumerate all constants
                - make sure they are listed in the matches
            - recursive:

        - analyze possible input values
    """


def eqtrans_v1(a : Expr, b : Expr, c : Expr):
    ideq(a, b) and ideq(b, c)
    return ideq(a, c)

def eqtrans_v2(eq1 : Eq, eq2 : Eq):
    match eq1, eq2: 
        case Eq(a,b1, cert=True), Eq(b2,c, cert=True) if b1 == b2:  return ideq(eq1, eq2)
        case _ : assert False

@magic
def eqtrans_v3(eq1 : Eq, eq2 : Eq):
    """ would like very much to write just 'b' without numbers but Python throws a SyntaxError
        missing stuff would be fixed by @magic decorator 
    """
    match eq1, eq2: 
        case Eq(a,b1, True),  Eq(b2,c, v=True) : Eq(a, c, True)
        case _                                 : assert False
