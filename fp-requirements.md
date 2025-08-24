# Requirements

## Functional Style

- Avoid imperative control flow (for, while, if as control flow).

- Prefer match statements for pattern matching

- Focus on ease of reasoning and provability over performance.

- Functions should always return total values, never raise exceptions or return None.

## Special Objects / Error Handling

- Use Empty[C] to represent an empty object of class C instead of None.

- Use Error object to represent search failures or computation errors.

- Any operation on an Error object returns itself.


## Parameter Naming

In function definitions, use lst as the parameter name for a single list.

- When a function has multiple parameters, use la, lb, etc.

- In function bodies and proofs, use x for the head of a list and xs for the tail.

## Docstring Style

Be concise in function docs.

- Refer to parameters as finite lists.

If the function has only one parameter, mention it just as “finite list” and do not repeat the parameter name.

- Avoid verbose stylistic descriptions in docs (e.g., no “recursively using purely functional style”).


## Concatenation

- Define cat(la, lb) as an inductive match-style function, only for proofs or when breaking things down inductively.

- In general usage, use + as syntactic sugar for concatenation.

## rev and Similar Functions

- Use + for concatenation in rev and other functions.

In proofs, use cat as the inductive reference if needed.

- Recursive functions like rev should follow match-style head/tail decomposition.

## Typing

- Include type annotations using the typing module (TypeVar, List, Callable, etc.).

## Readability & Mathematical Proofs

- Function definitions and proofs should align in naming (x / xs).

- Proofs should be easy to read, aligned with the function’s recursive decomposition.

- Use a functional/inductive style for reasoning and proofs.