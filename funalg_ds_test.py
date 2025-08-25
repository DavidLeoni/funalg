import pytest
from funalg import *

import funalg

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

    assert V('x') == V('x')
    assert V('a') != V('b')
    assert V('a') != V('x')
    
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

    
    
    


def test_tail():

    assert tail(L()) == Err()
    assert tail(L('a')) == EL
    assert tail(L('a', L('b'))) == L('b')
    assert tail(L('a', L('b', L('c')))) == L('b', L('c'))

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

    
    