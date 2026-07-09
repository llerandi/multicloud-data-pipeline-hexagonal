# PR 1: Domain model

Branch: `feature/domain-model`

Files added: `src/domain/models.py`, `src/domain/exceptions.py`,
`tests/domain/test_models.py`, `tests/domain/test_exceptions.py`.

## What this layer is allowed to know

`src/domain` imports nothing outside the Python standard library. No pandas,
no cloud SDK, no database driver. That restriction is the entire point of a
domain layer: it describes the business concepts (what is a valid dataset)
using only plain Python, so the rule can be tested and read without running
any infrastructure code.

## `QualityThresholds`: why a class instead of a constant

The business rule is "reject a dataset with more than 5% null values". The
naive way to write that is to hardcode `0.05` inside the method that checks
it. Instead, `QualityThresholds` is a small object that carries the number:

```python
@dataclass(frozen=True)
class QualityThresholds:
    max_null_ratio: float = 0.05
```

The reason is not aesthetics. A hardcoded number can only ever have one
value. An object can be constructed differently in different contexts
(stricter thresholds for a critical dataset, looser ones for an exploratory
one, a different value in tests) without touching the method that applies
the rule. The default of `0.05` is what the project uses today, not a limit
of what the code can express.

`frozen=True` makes instances immutable: once created, `max_null_ratio`
cannot be reassigned. That matters because this object is meant to be a
fixed input to a decision, not a piece of mutable state that could change
mid-calculation.

## `DataQualityReport`: a value object, not an entity

```python
@dataclass(frozen=True)
class DataQualityReport:
    total_rows: int
    null_count: int
    duplicate_count: int
    out_of_range_count: int
```

In domain-driven design terms, this is a value object rather than an entity.
An entity has an identity that persists even if its data changes (a customer
row keeps being "the same customer" if you update their address). A value
object has no identity at all, two `DataQualityReport` instances with the
same four numbers are simply equal, interchangeable, there is no sense in
which one of them is "more the same report" than the other. `@dataclass`
gives this for free: it generates `__eq__` based on field values, and
`frozen=True` prevents mutation after creation, which is what you want for
something that represents a snapshot of a measurement.

## `null_ratio`: a computed property, and the empty dataset guard

```python
@property
def null_ratio(self) -> float:
    if self.total_rows == 0:
        return 0.0
    return self.null_count / self.total_rows
```

Two things worth noticing here.

First, `null_ratio` is a `@property`, not a stored field. It is derived from
`null_count` and `total_rows`, so storing it separately would create a way
for the two numbers to disagree (imagine updating `null_count` and
forgetting to update a stored `null_ratio`). Deriving it on every access
makes that class of bug impossible.

Second, the `if self.total_rows == 0` guard exists because
`self.null_count / self.total_rows` would otherwise raise
`ZeroDivisionError` for an empty dataset. The choice made here is that an
empty dataset has a null ratio of `0.0`, not an error. This is a real design
decision, not a technicality: "zero rows" and "bad rows" are different
failure modes, and conflating them (by crashing on the first one while
checking for the second) would make the rule harder to reason about. Whether
an empty dataset should even reach this point in a real pipeline is a
separate question, handled elsewhere, not something this property should
decide by throwing an exception.

## `is_acceptable`: where the actual rule lives

```python
def is_acceptable(self, thresholds: QualityThresholds) -> bool:
    return self.null_ratio <= thresholds.max_null_ratio
```

This method takes the thresholds as a parameter instead of reading a global
constant. That is what makes it testable with different thresholds without
any patching or mocking, see `test_dataset_is_acceptable_at_exactly_the_threshold`
in the test file, which checks the boundary case (`null_ratio` exactly equal
to `max_null_ratio`) is accepted, not rejected. Boundary cases like `<=`
versus `<` are exactly the kind of decision that is easy to get backwards by
accident and easy to verify with one line of test.

## `DatasetRejectedError`: a business failure, not a technical one

```python
class DatasetRejectedError(Exception):
    def __init__(self, report: DataQualityReport, reason: str) -> None:
        self.report = report
        self.reason = reason
        super().__init__(reason)
```

This exception exists to be raised when a dataset fails the quality rule,
as opposed to, say, a network timeout talking to a storage bucket. Keeping
that distinction explicit in the domain layer means the application layer
can later decide to handle them differently (a rejected dataset gets a
notification with a reason, a network error might get retried).

It carries the `report` that caused the rejection, not just a string
message, so whoever catches this exception (a use case, eventually a
notification adapter) has access to the actual numbers (`null_ratio`, row
counts) instead of having to parse them back out of a message. `reason` is
kept as a separate, human-readable string because "explain why in one
sentence" and "expose the raw numbers" are two different needs, and a
`str(error)` should read naturally when printed or logged, which is why it
is passed to `super().__init__(reason)`.

## Why the tests include an empty-dataset and a boundary case

`tests/domain/test_models.py` does not only test the "obvious" case (10%
nulls, clearly rejected). It also tests total_rows=0 and null_count exactly
at the threshold. Both are the kind of input that is easy to forget when
writing the implementation and easy to get wrong (division by zero, `<`
instead of `<=`), so they are exactly the cases worth writing down as tests
rather than trusting memory.
