# PR 14: CloudMonitoringMetricsPublisher adapter

Branch: `feature/cloud-monitoring-metrics-publisher`

Files added:
`src/infrastructure/metrics/cloud_monitoring_metrics_publisher.py`,
`src/infrastructure/metrics/__init__.py` (updated),
`tests/infrastructure/metrics/test_cloud_monitoring_metrics_publisher.py`,
`pyproject.toml` (updated).

`MetricsPublisher` now has both adapters the project scope asked for:
console and Cloud Monitoring. This one required a genuinely different
kind of decision from every adapter before it, worth spelling out before
anything else in this file.

## Why this adapter cannot duck-type a single real SDK method the way the others do

Every adapter so far, Postgres, GCS, S3, BigQuery, was built around one
observation: the real client library already exposes a simple method
(`cursor().executemany()`, `blob().download_as_bytes()`,
`Object().get()`, `insert_rows_json()`) that takes plain arguments and
does the one thing the adapter needs, so this project's adapter could
call that same method on an injected object without ever importing the
SDK that defines it.

Cloud Monitoring does not have an equivalent. Writing a single custom
metric there means constructing a `TimeSeries` protobuf message, itself
containing a `MonitoredResource` and one or more `Point` objects, each
with a typed value and a start/end time interval, all built from classes
`google-cloud-monitoring` defines. There is no plain-argument method on
the real client this project could call without either building those
protobuf objects here (which means importing the SDK to do it) or asking
whoever injects the client to build them (which pushes real complexity
onto every caller).

## The choice made instead: define this project's own plain shape, and stop there

```python
@staticmethod
def _point(metric_name, value, labels):
    return {
        "metric_type": f"custom.googleapis.com/data_quality/{metric_name}",
        "value": value,
        "labels": labels,
    }
```

`CloudMonitoringMetricsPublisher` defines its own minimal shape for a
"point", a plain dict with a metric type string, a numeric value, and a
dict of labels, and calls one method, `client.write_points(project_name, points)`,
passing a list of these. This adapter's job stops there: deciding what
to publish and in what shape. Turning a list of these plain dicts into
real Cloud Monitoring `TimeSeries` objects, and actually calling
`create_time_series` on the real `MetricServiceClient`, is left to
whatever concrete `client` wrapper gets constructed and handed to this
class, not written in this PR.

This is a different, and slightly heavier, trade-off than every earlier
adapter's. `PostgresDatasetRepository` or `GcsFileStorage` hand a nearly
untouched call straight to a realistic stand-in for the real SDK object.
This adapter instead invents a shape of its own and defers the harder
translation work to a layer that does not exist yet. It is documented
here directly, rather than left implicit, because it is a meaningfully
different kind of gap than "we do not import the SDK for identifier
quoting" or "we do not translate a not-found exception", both of which
were about a missing detail. This one is about an entire translation
step this PR does not attempt to write, on purpose, rather than getting
it wrong by guessing at protobuf shapes without a working project to test
them against.

## Why one point per report field, not one point carrying every field

```python
points = [
    self._point("total_rows", report.total_rows, labels),
    self._point("null_count", report.null_count, labels),
    self._point("null_ratio", report.null_ratio, labels),
    self._point("duplicate_count", report.duplicate_count, labels),
    self._point("out_of_range_count", report.out_of_range_count, labels),
]
```

Cloud Monitoring itself models a metric as one named, timestamped
number. `null_ratio` and `duplicate_count` are two different metrics to
query, chart, or alert on independently later, not two fields inside one
blob a dashboard would need to parse apart first. Publishing five
separate points, all sharing the same `dataset` label, matches how Cloud
Monitoring expects to receive this data, and keeps
`ConsoleMetricsPublisher` and this adapter working from the exact same
`DataQualityReport`, just presenting its fields differently.

## Why `dataset_name` becomes a label, not part of the metric name

`{"dataset": dataset_name}` is attached to every point instead of baking
the dataset name into the metric type itself (something like
`custom.googleapis.com/data_quality/customers_null_ratio`). Labels are
how Cloud Monitoring expects a metric to be sliced by dimension, a fixed
set of metric types (`null_ratio`, `duplicate_count`, and so on) each
carrying a `dataset` label is what makes "show me `null_ratio` across
every dataset" or "show me `null_ratio` for `customers` only" both
answerable from the same data, folding the dataset name into the metric
type itself would make the first question require knowing every dataset
name in advance.

## `google-cloud-monitoring` as its own `monitoring` extra

Same pattern as every dependency before it: its own optional extra in
`pyproject.toml`, so installing for work unrelated to this adapter stays
light.
