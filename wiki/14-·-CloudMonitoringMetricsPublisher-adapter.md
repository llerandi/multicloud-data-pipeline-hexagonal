# 14 · CloudMonitoringMetricsPublisher adapter

Branch: `feature/cloud-monitoring-metrics-publisher` · Technical write-up:
[docs/14-cloud-monitoring-metrics-publisher.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/14-cloud-monitoring-metrics-publisher.md)

## The concept this stage teaches

`MetricsPublisher` now has both adapters the scope asked for, and this
one breaks the pattern every adapter since
[09](09-·-SklearnModelInference-adapter) has relied on. Postgres, GCS, S3,
BigQuery all worked because the real SDK exposes one plain-argument
method that does exactly what the adapter needs - duck-typing that one
call was enough to avoid importing the SDK entirely. Cloud Monitoring has
no equivalent: publishing a metric means building a `TimeSeries` protobuf
message with a `MonitoredResource` and one or more typed `Point` objects,
classes only `google-cloud-monitoring` defines. There's no single
plain-argument method here to duck-type.

## What to notice

- The adapter's answer is to invent its own minimal shape instead - a
  plain dict `{"metric_type": ..., "value": ..., "labels": ...}` - and
  call one method, `client.write_points(...)`, on the injected client.
  Turning those dicts into real `TimeSeries` objects is left to whatever
  concrete client wrapper gets built later, not attempted here. This is a
  heavier, different trade-off than every earlier adapter's, and it's
  named as such directly in the write-up rather than left implicit.
- One point is published per report field (`total_rows`, `null_ratio`,
  `duplicate_count`, ...) instead of one point carrying the whole report
  - because Cloud Monitoring itself models a metric as one named,
  timestamped number, not a blob a dashboard would need to parse apart.
- `dataset_name` becomes a **label** on every point, not part of the
  metric name - that's what makes "show me `null_ratio` across every
  dataset" and "show me `null_ratio` for `customers` only" both
  answerable from the same data.

## Why it matters for the rest of the project

Read this page right after [09](09-·-SklearnModelInference-adapter)
through [13](13-·-BigqueryDatasetRepository-adapter) - the contrast is
the point. Hexagonal architecture doesn't promise every adapter looks the
same; it promises the *use case* never has to care which shape of
trade-off a given adapter made. The real `TimeSeries` translation is
still open work - see [Roadmap](Roadmap-and-status).

Back to [Home](Home) · Previous: [13 · BigqueryDatasetRepository adapter](13-·-BigqueryDatasetRepository-adapter) · Next: [15 · SlackNotificationPort adapter](15-·-SlackNotificationPort-adapter)
