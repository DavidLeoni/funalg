# Proof Verifier Requirements

## Stakeholders:

- System designer
    - trusted
    - writes *_axiom functions, datatypes

- Proof engineer 
    - untrusted
    - writes *_thm functions

## Data types

Everything is an `Expr`

- vars
- single char literals 'a', 'b', 'c', ... (for now, later we'll consider full strings)
- immutable lists: we reuse Python lists and ban mutable methods

Integer numbers constructed from `0`, `1` and `+`: 

- 0
- 1 == 1 + 0
- 2 == 1 + (1 + 0)
- 3 == 1 + (1 + (1 + 0))

`+` is intended as synctactic sugar for:


class Nat(ListExpr):
    pass

def plus_nat(n : Nat, m : Nat):
    match m:
        case Zero:
            return n
        case Nat(One, *rest)



- Proofs should be automatically testable
- the Proof engineer cannot be trusted to write a correct proof
- Proof engineer writes proof as a function structured like this:

input: assumptions as symbolic expressions
output: a symbolic expression ret which should always have truthy value `True`

To ensure these constraints, for now we trust the proof engineer will always end the proof function with:

```python
assert ret
return ret
```

- in the *_thm functions, manual creation of `Expr` with `certified=True` should never be allowed. The only way to obtain them should be via calls to other `*_thm` or `*_axiom` functions 

- The only Expr with certified=True can be: - literal ones (constants, lists with constants, ...) - expressions produced by theorem functions with zero parameters, or foundational theorem functions with parameters we decide to implement, but in that case we will call them *_axiom

