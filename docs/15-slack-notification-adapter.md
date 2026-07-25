# PR 15: SlackNotificationPort adapter

Branch: `feature/slack-notification-adapter`

Files added: `src/infrastructure/notifications/slack_notification_port.py`,
`src/infrastructure/notifications/__init__.py` (updated),
`tests/infrastructure/notifications/test_slack_notification_port.py`,
`pyproject.toml` (updated).

`NotificationPort` now has both adapters the project scope asked for:
a log stub and Slack. After `CloudMonitoringMetricsPublisher` needed a
genuinely different approach, this one is worth noting for the opposite
reason: it goes back to the normal pattern.

## Back to one simple, duck-typed method

```python
"""
Back to the same pattern as most adapters before
CloudMonitoringMetricsPublisher: sending a Slack message [...] comes
down to one call that takes a plain string.
"""
```

Whether a real implementation sends through an incoming webhook (a
single HTTP POST with a JSON body) or through `slack_sdk`'s
`WebClient.chat_postMessage`, the actual operation this project cares
about is "send this text somewhere". `SlackNotificationPort` calls
`client.send(message)`, one method, one string argument, and does not
import `slack_sdk` or make an HTTP request itself, same reasoning as
`PostgresDatasetRepository`'s connection or `GcsFileStorage`'s bucket:
testable with a fake, no real Slack workspace needed to run these tests.
Cloud Monitoring's adapter was the exception in this project, not a new
rule, this one confirms that.

## Why the message uses Slack's own markup, when nothing else in the project does

```python
message = f":warning: dataset `{dataset_name}` rejected: {reason}"
```

`LogStubNotificationPort`'s message is plain text passed to
`logger.warning`, `ConsoleMetricsPublisher`'s output is a plain
key=value line. Neither destination, a log aggregator or a terminal,
renders markup, so neither adapter uses any. Slack does: backticks
render `dataset_name` in a monospace font, `:warning:` renders as an
emoji, both using Slack's own lightweight `mrkdwn` convention. This is
the one adapter in the project so far where the message's destination
has its own formatting convention worth using, and the only place that
formatting shows up.

## Same extras pattern, `slack_sdk` included even though unused directly

```toml
slack = [
    "slack_sdk>=3.27",
]
```

Same reasoning as every earlier adapter: `slack_sdk` is what whoever
builds a real `client` (wrapping either the Web API or an incoming
webhook) will need, even though `slack_notification_port.py` itself
never imports it, and it gets its own extra so installing for unrelated
work stays light.

## What is left after this PR

`NotificationPort` and `MetricsPublisher` are both fully covered now,
alongside `FileStorage` and `DatasetRepository` from earlier PRs. The
only port with an adapter still missing is `ModelInferencePort`'s Vertex
AI side, the local scikit-learn adapter already exists from PR 9.
