import pytest
from funalg import *
import funalg

def test_tail():

    assert tail(L()) == Err()
    assert tail(L('a')) == EL
    assert tail(L('a', L('b'))) == L('b')
    assert tail(L('a', L('b', L('c')))) == L('b', L('c'))


def test_head():
    
    assert head(L()) == Err()
    assert head(L('a')) == 'a'
    assert head(L('a', L('b'))) == 'a'
    assert head(L('a', L('b', L('c')))) == 'a'
    assert head(L(L('a'))) == L('a')

    
    