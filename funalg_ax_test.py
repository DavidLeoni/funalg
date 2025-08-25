import pytest
from funalg import *
import funalg
from funalg_ax import *
import funalg_ax

funalg.debug_show_certificate = True

def test_ideq():
        
    assert ideq(True, True) == Eq(True, True, certificate=True)
    assert ideq(False, False) == Eq(False, False, certificate=True)

    assert ideq([], []) == Eq([], [], certificate=True)
    assert ideq(L(), L()) == Eq(L(), L(), certificate=True)
    assert ideq(L('a'), L('a')) ==  Eq(L('a'), L('a'), certificate=True)
    
    with pytest.raises(AssertionError):
        ideq(True, False)

    with pytest.raises(AssertionError):
        ideq(False, True)

def test_not_false_ax():
    assert not_false_ax(False) == Not(False, certificate=True)
    
    with pytest.raises(AssertionError):
        not_false_ax(True)

def test_not_true_ax():
    assert not_true_ax(True) == Eq(Not(True), False, certificate=True)
    
    with pytest.raises(AssertionError):
        not_true_ax(False)



def test_subst_eq():
    print("***** CIAO")
    print(subst_eq(ideq(True, True), not_true_ax))
    print(Eq(Not(True), False, certificate=True))
    assert subst_eq(ideq(True, True), not_true_ax) == Eq(Not(True), False, certificate=True)

    assert verified(not_false_ax(False))

    assert subst_eq(Eq(False, Not(True), certificate=True), not_false_ax) \
           == Not(Not(True), certificate=True)
