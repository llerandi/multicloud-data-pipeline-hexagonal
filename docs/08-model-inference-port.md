# PR 8: ModelInferencePort

Branch: `feature/model-inference-port`

Files added: `src/application/ports/model_inference_port.py`,
`src/application/ports/__init__.py` (updated),
`tests/application/ports/test_ports.py` (updated).

Same pattern as the other four ports (PR 3), an `abc.ABC` with one
`abstractmethod`, no implementation. See `docs/03-application-ports.md`
for the full explanation of why `abc` is used, why the type hints stay
generic, and why the tests only check "cannot instantiate" plus "a
minimal concrete subclass works". This file only covers what is new or
different about this specific port.

## Why this port is optional, and the other four are not

```python
"""
Unlike the other four ports, this one is optional in the pipeline: the
use case only calls it if the dataset was accepted by the quality rule.
A dataset that fails validation never reaches a model.
"""
```

`FileStorage`, `DatasetRepository`, `MetricsPublisher` and
`NotificationPort` are all used on every run of
`ValidateAndIngestDataset`, on the success path or the failure path.
`ModelInferencePort` is different: the project scope describes it as a
step that runs "only if the dataset passes validation". That is stated
directly in the port's docstring so it stays documented at the contract
level, not only inside whichever use case ends up calling `predict`,
this port itself does not enforce the rule (an `abc.ABC` cannot enforce
when a method gets called, only that it exists), but the intent is
written down where anyone implementing or calling it will read it.

Wiring `predict` into `ValidateAndIngestDataset` (or a new use case) is
left for a later PR, once at least one real adapter (the local
scikit-learn one) exists to call it with.

## Why `predict` also takes `dataset_name`

```python
@abstractmethod
def predict(
    self, dataset_name: str, rows: Sequence[Mapping[str, Any]]
) -> Sequence[Any]:
```

`DatasetRepository.save` and `MetricsPublisher.publish` both take
`dataset_name` alongside their main argument. `predict` follows the same
shape, even though the local scikit-learn adapter will not need it (a
single local model does not care what the dataset is called). The
reason to include it now: a Vertex AI adapter very plausibly does need
it, to route to a different deployed endpoint depending on which dataset
is being processed, and adding a parameter to an existing abstract method
later is a breaking change for every adapter and every caller. Since the
port is being defined once, before any real adapter exists, it costs
nothing to shape it for the adapter that will need it, and the adapter
that does not need it simply ignores the argument.

## Why the return type is `Sequence[Any]`, not something more specific

A prediction could be a class label, a probability, a score, or a
dictionary bundling several of those. Different models produce
different shapes of output, and this port is not the place to guess
which one a specific model will use, that decision belongs to whichever
adapter wraps a specific model. `Any` is the honest type here: it does
not pretend to know something it cannot know yet, unlike `list[dict]` on
`DatasetRepository.save`, where a mapping actually is the right shape for
every case the project needs.
