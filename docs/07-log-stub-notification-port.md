# PR 7: LogStubNotificationPort adapter

Branch: `feature/log-stub-notification-port`

Files added: `src/infrastructure/notifications/log_stub_notification_port.py`,
`src/infrastructure/notifications/__init__.py` (updated),
`tests/infrastructure/notifications/test_log_stub_notification_port.py`.

## What this adapter is for

`LogStubNotificationPort` implements `NotificationPort` by writing to the
standard `logging` module instead of sending a Slack message or an email.
Like the other two dev-only adapters already in the project, it exists so
the pipeline has somewhere to send a failure notification before a real
Slack or email adapter is written, and so tests can assert on what would
have been sent without any network call happening.

## Why `logging`, not `print`, unlike `ConsoleMetricsPublisher`

The original scope described the metrics adapter as one that "just prints
to console" and this one as a stub that "only logs". That is not
accidental wording, and this PR keeps the distinction rather than making
both adapters use `print` for consistency.

A rejected dataset is an event someone might reasonably want to filter by
severity, route to a log aggregator, or silence in a specific
environment, all things `logging` supports and a bare `print()` call does
not. Metrics, as implemented so far, are closer to a running readout of
numbers, `print` fits that today. If `MetricsPublisher`'s console adapter
ever needs the same filtering or routing, switching it to `logging` later
is a small, contained change, not something this PR needs to force
prematurely.

## Two small `logging` conventions worth naming

```python
logger = logging.getLogger(__name__)

class LogStubNotificationPort(NotificationPort):
    def notify_failure(self, dataset_name: str, reason: str) -> None:
        logger.warning("dataset %s rejected: %s", dataset_name, reason)
```

`logging.getLogger(__name__)` at module level, not inside the class, is
the standard pattern, it names the logger after the module it lives in
(`src.infrastructure.notifications.log_stub_notification_port`), which is
what shows up in log output and lets someone configure logging
per-module later without touching this file.

`logger.warning("dataset %s rejected: %s", dataset_name, reason)` passes
`dataset_name` and `reason` as separate arguments rather than building an
f-string first. This is `logging`'s own convention: the module only does
the string interpolation if the message actually gets emitted at the
current log level, an f-string would always be built, even if warnings
are disabled entirely. It also means log aggregation tools that group
messages by their format string see one recurring message
(`"dataset %s rejected: %s"`), not a different string every time because
the values are already inlined.

`WARNING`, not `ERROR`, is the chosen level. A dataset getting rejected is
the business rule doing exactly what it is supposed to do, not a bug or a
crash in the pipeline. `ERROR` is reserved, at least in this project's
convention going forward, for the pipeline itself failing to run
correctly.

## What the tests check, using `caplog`

```python
def test_notify_failure_logs_one_warning_with_dataset_name_and_reason(caplog):
    with caplog.at_level(logging.WARNING):
        notifier.notify_failure("customers", "null ratio 0.20 exceeds max 0.05")

    assert caplog.records[0].levelname == "WARNING"
    assert "customers" in caplog.text
```

`caplog` is the `logging` equivalent of the `capsys` fixture used for
`ConsoleMetricsPublisher`, it captures log records emitted during a test
instead of the real ones going wherever this project's logging is
otherwise configured to send them. `caplog.at_level(logging.WARNING)`
sets the minimum level being captured for that block.

A second test calls `notify_failure` again, but with `caplog.at_level(logging.ERROR)`,
a stricter filter than the `WARNING` level this adapter actually logs at,
and checks nothing was captured. This exists to lock in the level choice
itself: if `notify_failure` were changed to log at `INFO` or `DEBUG` by
accident, this test would not catch that on its own, but if it were
changed to log at `ERROR` when it should not, a test checking only "some
warning happened" would not catch a level regression either. Testing both
"a WARNING happens" and "nothing happens above WARNING" pins the level
down from both sides.
