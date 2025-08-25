import pytest
from funalg import *
import funalg
from funalg_thm import *
import funalg_thm

funalg.debug_show_certified = True


def test_not_not():
    """ Note this is an exhaustive test!
    """
    case1 = not_not(Not(Not(True)))
    assert case1 == Eq(Not(Not(True)), True, certificate=True)
    case2 = not_not(Not(Not(False)))
    assert case1 == Eq(Not(Not(False)), False, certificate=True)
    #assert case1 == case2      can't be..
    