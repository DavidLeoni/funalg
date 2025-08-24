import pytest
from funalg import *
import funalg
from funalg_ax import *
import funalg_ax

funalg.debug_show_certified = True

def test_ideq():
        
    assert ideq(True, True) == Eq(True, True, certified=True)
    assert ideq(False, False) == Eq(False, False, certified=True)

    assert ideq([], []) == Eq([], [], certified=True)
    assert ideq(L(), L()) == Eq(L(), L(), certified=True)
    assert ideq(L('a'), L('a')) ==  Eq(L('a'), L('a'), certified=True)
    
    with pytest.raises(AssertionError):
        ideq(True, False)

    with pytest.raises(AssertionError):
        ideq(False, True)

def test_not_false_ax():
    assert not_false_ax(False) == Not(False, certified=True)
    
    with pytest.raises(AssertionError):
        not_false_ax(True)

def test_not_true_ax():
    assert not_true_ax(True) == Eq(Not(True), False, certified=True)
    
    with pytest.raises(AssertionError):
        not_true_ax(False)


def test_subst_eq():
    print("***** CIAO")
    print(subst_eq(ideq(True, True), not_true_ax))
    print(Eq(Not(True), False, certified=True))
    assert subst_eq(ideq(True, True), not_true_ax) == Eq(Not(True), False, certified=True)

    assert verified(not_false_ax(False))

    assert subst_eq(Eq(False, Not(True), certified=True), not_false_ax) \
           == Not(Not(True), certified=True)
