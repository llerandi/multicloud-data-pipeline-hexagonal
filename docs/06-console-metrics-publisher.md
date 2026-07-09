# PR 6: ConsoleMetricsPublisher adapter

Branch: `feature/console-metrics-publisher`

Files added: `src/infrastructure/metrics/console_metrics_publisher.py`,
`src/infrastructure/metrics/__init__.py` (updated),
`tests/infrastructure/metrics/test_console_metrics_publisher.py`.

## What this adapter is for

`ConsoleMetricsPublisher` implements `MetricsPublisher` by printing the
report to stdout. Like `LocalFileStorage`, it is not meant for
production, it exists so the pipeline has somewhere to send its metrics
before a real Cloud Monitoring adapter is written, and so that adapter,
once it exists, has the same contract to be compared against.

## Why key=value pairs on one line, and why `print` instead of `logging`

```python
def publish(self, dataset_name: str, report: DataQualityReport) -> None:
    print(
        f"[metrics] dataset={dataset_name} "
        f"total_rows={report.total_rows} "
        ...
    )
```

The original project scope describes this adapter as "one that just
prints to console, for dev", so `print` is used directly rather than
Python's `logging` module. `logging` would add real value in a
production adapter (log levels, handlers, structured output
configuration), but for a class whose entire job is "show the numbers to
whoever is watching the terminal right now", it would be a layer of
configuration this project does not need yet.

The one-line, key=value format is a small deliberate choice too: it
reads naturally to a person watching a terminal scroll by, and it is
still easy to grep or parse later (`grep "dataset=customers"`) without
needing a real structured logging pipeline. `report.null_ratio:.2%` uses
the same percentage formatting as the rejection reason string in the use
case, so the same number reads the same way wherever it shows up.

## What the tests check, using `capsys`

```python
def test_publish_prints_the_dataset_name_and_report_fields(capsys):
    ...
    captured = capsys.readouterr()
    assert "total_rows=100" in captured.out
```

`capsys` is a built-in pytest fixture that captures whatever a test
writes to stdout (and stderr), instead of letting it actually print to
the terminal during the test run. That is what makes it possible to
assert on the actual printed text, catching, for example, a typo in a
field name or a forgotten field, rather than only checking that
`publish` did not raise an exception.

A second test calls `publish` twice and checks the output is exactly two
lines, one per call, each naming the right dataset. This guards against
an easy mistake for this specific kind of adapter: accidentally using
`print(..., end="")` or otherwise merging multiple calls onto one line,
which would still "work" but would make the printed output unreadable
once more than one dataset gets processed in the same run.
