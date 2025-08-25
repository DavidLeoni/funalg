from typing import TypeVar, Generic, List, Callable, Union, Any, Iterable, TypeVarTuple

T = TypeVar("T")  
U = TypeVar("U")
Ts = TypeVarTuple("Ts")

class A(Generic[*Ts]):
    pass

class B(Generic[*Ts, T], A[[*Ts,T]]):
    pass

class C(A[T]):
    pass

class D(Generic[*Ts, T], C[B[*Ts, T]]):
    pass