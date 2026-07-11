# 07 · LogStubNotificationPort adapter

Branch: `feature/log-stub-notification-port` · Technical write-up:
[docs/07-log-stub-notification-port.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/07-log-stub-notification-port.md)

## The concept this stage teaches

Two adapters for two different ports (this one, and stage 06's
`ConsoleMetricsPublisher`) both exist purely as dev-time stand-ins for a
real integration (Slack/email, and Cloud Monitoring, respectively). The
useful lesson here is that "dev-only adapter" doesn't mean "don't think
about the implementation" - this one deliberately uses `logging` instead
of `print`, because a rejected dataset is an event someone might want to
filter by severity or route somewhere, unlike a metrics readout.

## What to notice

- `logger = logging.getLogger(__name__)` at module level is the standard
  convention - it names the logger after the module, which is what shows
  up in output and what lets logging be configured per-module later.
- `logger.warning("dataset %s rejected: %s", dataset_name, reason)` passes
  values as separate arguments, not an f-string - `logging` only does the
  interpolation if the message is actually emitted at the current level,
  and log aggregators can group by the recurring format string instead of
  seeing a different string every time.
- `WARNING`, not `ERROR`, is the chosen level - a dataset getting rejected
  is the business rule working as intended, not a bug. This project
  reserves `ERROR` for the pipeline itself failing to run.
- Tests use `caplog` (the `logging` equivalent of `capsys`) and pin the
  level down from both directions: one test proves a `WARNING` happens,
  another proves nothing happens at `ERROR` - together they catch a level
  regression in either direction.

## Why it matters for the rest of the project

This page pairs with [06 · ConsoleMetricsPublisher](06-Console-Metrics-Publisher):
same "temporary dev adapter" role, deliberately different tool choice.
Worth revisiting once a real Cloud Monitoring adapter exists - see
[Roadmap](Roadmap) for that open question.

Back to [Home](Home) · Previous: [06 · ConsoleMetricsPublisher adapter](06-Console-Metrics-Publisher) · Next: [08 · ModelInferencePort](08-Model-Inference-Port)
