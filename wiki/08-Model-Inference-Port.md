# 08 · ModelInferencePort

Branch: `feature/model-inference-port` · Technical write-up:
[docs/08-model-inference-port.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/08-model-inference-port.md)

## The concept this stage teaches

Same mechanical pattern as stage 03 (`abc.ABC` + one `abstractmethod`, no
implementation) - but this port is *optional*: the use case only calls it
if a dataset passed validation. The interesting part is where that "only
sometimes" rule gets documented. An `abc.ABC` has no way to enforce *when*
a method is called, only that it exists - so the optionality is written
into the port's own docstring instead, at the contract level, where anyone
implementing or calling it will actually read it.

## What to notice

- `predict` takes `dataset_name` even though the first real adapter (local
  scikit-learn) won't need it - because a later Vertex AI adapter
  plausibly will, to route to different deployed endpoints per dataset.
  Adding a parameter to an existing abstract method later breaks every
  adapter and caller, so the port is shaped up front for the adapter that
  will need it.
- The return type is `Sequence[Any]`, not something more specific - a
  prediction's shape (label, probability, score, dict of several) depends
  on the model, and the port isn't the place to guess which one. `Any`
  here is an honest type, not a lazy one, unlike `list[dict]` on
  `DatasetRepository.save`, where a mapping really is the right shape for
  every case this project needs.
- Wiring `predict` into the actual use case is deliberately deferred to a
  later PR, once a real adapter exists to call it with - see
  [Roadmap](Roadmap).

## Why it matters for the rest of the project

This is the last port defined so far. Everything from here is
implementation: real cloud adapters for the four ports from stage 03, plus
the first real adapter for this one. See [Roadmap](Roadmap) for what's
next.

Back to [Home](Home) · Previous: [07 · LogStubNotificationPort adapter](07-Log-Stub-Notification-Port)
