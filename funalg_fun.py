""" Functions
"""

from funalg import *

import funalg


def tail(lst: L) -> L:
    match lst:
        #case L():   # can't use it because of weird Python __match_args__ rules
        case       []:  return Err()    # ok because our L is also a collection.abc.Sequence
        case [x, *xs]:  return L(xs)

Tail = FunDef(  V("tail"),
                Fun(    L(V("lst")), 
                
                        Match(V("lst"), 
                            Case(   EL,
                                    Return(Err)),

                            Case(   L(V("x"), Rest(V("xs"))), 
                                    Return(V("xs")))
                            )
                    )
)
        


def head(lst: L) -> L:
    match lst:
        case        []: return Err()
        case  [x, *xs]: return x
