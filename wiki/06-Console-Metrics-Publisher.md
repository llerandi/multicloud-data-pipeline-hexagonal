# 06 · ConsoleMetricsPublisher adapter

Branch: `feature/console-metrics-publisher` · Technical write-up:
[docs/06-console-metrics-publisher.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/06-console-metrics-publisher.md)

## The concept this stage teaches

The second adapter in the project, and the useful thing to notice is what
*doesn't* change: `ValidateAndIngestDataset` from stage 04 needed zero
modifications to gain a `MetricsPublisher` implementation. This is the
payoff of stage 03 (ports) made concrete a second time - a different port,
same pattern, same guarantee.

## What to notice

- `print` is used deliberately, not `logging` - the docstring in the
  original scope calls this adapter "one that just prints to console, for
  dev." A production adapter (Cloud Monitoring) would warrant `logging`'s
  levels and handlers; this dev-only one doesn't need that configuration
  layer yet.
- The tests use `capsys`, a pytest fixture that captures stdout instead of
  letting it print during the test run - this is what lets a test assert
  on the *exact* printed text, catching a typo'd field name that "it
  didn't raise" would miss.
- A second test checks two calls to `publish` produce exactly two lines -
  guarding against a specific, easy mistake (`print(..., end="")`) that
  would still "work" but merge output unreadably.

## Why it matters for the rest of the project

Compare this page with [07](07-Log-Stub-Notification-Port): both are
dev-only stand-ins for a port, and both were deliberately built
*differently* (`print` here, `logging` there) because the events they
represent are different in kind. That contrast is worth sitting with - it
shows hexagonal architecture doesn't force every adapter for every port to
look the same, only that each one honestly fulfills its contract.

Back to [Home](Home) · Previous: [05 · LocalFileStorage adapter](05-Local-Filesystem-Adapter) · Next: [07 · LogStubNotificationPort adapter](07-Log-Stub-Notification-Port)
