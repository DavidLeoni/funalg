import pytest
from funalg import *


import funalg

from typing import Literal, Union, Tuple
from enum import Enum


class T:
    __match_args__ = ("p",)
    def __init__(self, p='a'):
        self.p = p

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.p == other.p

def test_match():
    """ Shows we need stupid __match_args__ attr in classes, if not present assert m2 fails

        Notice it wouldn't be necessary if we used data classes.
    """


    t1 = T()
    match t1:
        case T():
            m1 = True
        case T('b'):
            m1 = False
    assert m1

    t2 = T('b')
    match t2:
        case T('a'):
            m2 = False
        case T('b'):
            m2 = True
    assert m2

def test_CExpr_copy():
    """ TODO """
    ex1 = CExpr(cert=True)
    #c = ex1.copy()
    #assert c.cert is True
    
def test_L_match_structural():
    """ Shows we need stupid __match_args__ attr in classes, if not present assert m2 fails

        Notice it wouldn't be necessary if we used data classes.
    """

    l1 = L()
    match l1:
        case L():
            m1 = True
        case L('b'):
            m1 = False
    assert m1

    l2 = L('b')
    match l2:
        case L('a'):
            m2 = False
        case L('b'):
            m2 = True
    assert m2

    l3 = L('a', L('b'))
    match l3:
        case funalg.EL:
            m3 = False
        case L('a'):
            m3 = False
        case L('a', L('b')):
            m3 = True
    #assert m3  # I would like this assert to pass, unfortunately python matching doesn't work the way I'd like  
    assert not m3  #  sic  :-(

def test_L_match_as_sequence():

    l1 = L()
    match l1:
        case []:
            m1 = True
        case ['b']:
            m1 = False
    assert m1

    l2 = L('b')
    match l2:
        case ['a']:
            m2 = False
        case ['b']:
            m2 = True
    assert m2

    l3 = L('a', L('b'))
    match l3:
        case funalg.EL:
            m3 = False
        case ['a']:
            m3 = False
        case ['a', 'b']:
            m3 = True
    assert m3



def test_L_repr():
    assert repr(L()) == 'L()'
    assert repr(L('a')) == "L('a')"
    assert repr(L('a', L('b'))) == "L('a', L('b'))"
     

def test_L_init_head_tail():

    la = L('a')
    assert la.head == 'a'
    assert la.tail is None
    
    lab = L('a', L('b'))
    assert lab.head == 'a'
    assert lab.tail.head == 'b'
    assert lab.tail.tail is None

    assert L() == L()
    assert L() == EL
    assert L("a") == L("a")
    assert L("a") != L("A")
    assert L() != L("a")
    assert L() != L("a", L("b"))
    assert L("a") != L()
    assert L("a", L("b")) != L()

    assert L("a", L("b")) == L("a", L("b"))
    assert L("a", L("b", L("c"))) == L("a", L("b", L("c")))


    with pytest.raises(ValueError):
        L([], 'a')
    with pytest.raises(ValueError):
        L([], ['a'])
    with pytest.raises(ValueError):
        L(['a'], 'b')
    with pytest.raises(ValueError):
        L(['b'], ['b'])

def test_L_init_seq():

    lv = L([])
    assert lv.head is None
    assert lv.tail is None


    la = L(['a'])
    assert la.head is 'a'
    assert la.tail is None

    lab = L(['a', 'b'])
    assert lab.head is 'a'
    assert lab.tail.head is 'b'
    assert lab.tail.tail is None
    

    assert L([]) == L()
    assert L(['a']) == L('a')
    assert L(['a', 'b']) == L('a', L('b'))
    assert L(['a', 'b', 'c']) == L('a', L('b', L('c')))
    
    

def test_L_len():
    assert len(L()) == 0
    assert len(L('a')) == 1
    assert len(L('a', L('b'))) == 2
    assert len(L('a', L('b', L('c')))) == 3


def test_L_truthy_falsy():
    """ Note: we don't override __bool__ as we already override __len__ and Python automatically uses that """
    assert L('a')
    assert L('a', L('b'))
    assert bool(L()) is False
    assert bool(L('a')) is True
    assert not L()

def test_L_iter():
    
    l0 = L()
    assert list(l0) == []

    l1 = L('a')
    assert list(l1) == ['a']

    l2 = L('a', L('b'))
    assert list(l2) == ['a', 'b']

    l3 = L('a', L('b', L('c')))
    assert list(l3) == ['a', 'b', 'c']

def test_L_getitem():

    l0 = L()

    with pytest.raises(IndexError):
        l0[0]


    with pytest.raises(IndexError):
        l0[1]

    l1 = L('a')
    assert l1[0] == 'a'

    with pytest.raises(IndexError):
        l1[1]

    with pytest.raises(IndexError):
        l1[-1]


    l2 = L('a', L('b'))
    assert l2[0] == 'a'
    assert l2[1] == 'b'


    l3 = L('a', L('b', L('c')))
    assert l3[0] == 'a'
    assert l3[1] == 'b'
    assert l3[2] == 'c'

    

def test_V():
    global debug_show_cert
    assert V('x') == V('x')
    assert V('a') != V('b')
    assert V('a') != V('x')


    assert V('x', int) == V('x', int)
    assert V('x', int) != V('x', bool)

    assert V('a', int) != V('b', int)
    assert V('a', int) != V('x', int)

    old = debug_show_cert
    debug_show_cert = True
    assert repr(V('a')) == "V('a')"
    assert repr(V('a',int)) == "V('a',int)"
    assert repr(V('a',int,cert=True)) == "V('a',int,cert=True)"
    assert repr(V('a',int,cert=False)) == "V('a',int,cert=False)"
    assert repr(V('a',int,cert=None)) == "V('a',int)"
    debug_show_cert = old

    with pytest.raises(Exception):
        seval(V('x'), {})



def test_get_cert():

    assert get_cert(True) is True
    assert get_cert(False) is False
    assert get_cert(None) is None
    assert get_cert("umpalumpa") is None
    assert get_cert(CExpr()) is None
    assert get_cert(CExpr(cert=True)) is True
    assert get_cert(CExpr(cert=False)) is False

def test_certified():

    assert certified(True) is True
    assert certified(False) is True
    assert certified(None) is False
    assert certified("umpalumpa") is False
    assert certified(CExpr()) is False
    assert certified(CExpr(cert=True)) is True
    assert certified(CExpr(cert=False)) is True


def test_verified():

    assert verified(True) is True
    assert verified(False) is False
    assert verified(None) is False
    assert verified("umpalumpa") is False
    assert verified(CExpr()) is False
    assert verified(CExpr(cert=True)) is True
    assert verified(CExpr(cert=False)) is False

def test_falsified():

    assert falsified(True) is False
    assert falsified(False) is True
    assert falsified(None) is False
    assert falsified("umpalumpa") is False
    assert falsified(CExpr()) is False
    assert falsified(CExpr(cert=True)) is False
    assert falsified(CExpr(cert=False)) is True



def test_eq_eq():
    assert Eq(Not(True),False,cert=True) == Eq(Not(True),False,cert=True)


def test_not_expr():
    n = Not(True)
    assert n.e is True
    assert n.cert is False
    
    n = Not(False)
    assert n.e is False
    assert n.cert is True

    n = Not(True, cert=False)
    assert n.e is True
    assert n.cert is False

    n = Not(False, cert=True)
    assert n.e is False
    assert n.cert is True

    with pytest.raises(ValueError):
        n = Not(True, cert=True)

    with pytest.raises(ValueError):
        n = Not(False, cert=False)

    
def test_ebool():
    """ TODO not sure EBool is needed """ 
    
    assert not (TRUE  is True)
    assert not (FALSE  is False)    
    

    assert bool(TRUE)  is True
    assert bool(FALSE) is False
    
    assert (not FALSE) is True

    assert repr(TRUE)  == 'TRUE'
    assert repr(FALSE) == 'FALSE'
    
    assert TRUE == True
    assert TRUE != False
    
    assert FALSE == False
    assert FALSE != True
    
def test_enumerate_finite_type():

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert enumerate_finite_type(Literal["x", "y"]) == ["x", "y"]
    assert enumerate_finite_type(bool) == [True, False]
    assert set(enumerate_finite_type(bool | None)) == {True, False, None}
    assert set(enumerate_finite_type(Union[bool, None])) == {True, False, None}
    assert set(enumerate_finite_type(Tuple[Literal[1, 2], Color])) == {
        (1, Color.RED),
        (1, Color.GREEN),
        (1, Color.BLUE),
        (2, Color.RED),
        (2, Color.GREEN),
        (2, Color.BLUE),
    }

