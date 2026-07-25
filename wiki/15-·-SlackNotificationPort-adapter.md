# 15 · SlackNotificationPort adapter

Branch: `feature/slack-notification-adapter` · Technical write-up:
[docs/15-slack-notification-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/15-slack-notification-adapter.md)

## The concept this stage teaches

`NotificationPort` now has both adapters the project scope asked for, and
this one is worth reading right after [14](14-·-CloudMonitoringMetricsPublisher-adapter)
for the contrast: Cloud Monitoring was the exception, not a new rule.
Sending a Slack message, whether through an incoming webhook or
`slack_sdk`'s `WebClient.chat_postMessage`, comes down to one call that
takes a plain string. `SlackNotificationPort` calls `client.send(message)`
and stops there - back to the normal duck-typing pattern used since
[09](09-·-SklearnModelInference-adapter), no `slack_sdk` import, testable
with a fake, no real Slack workspace needed.

## What to notice

- The message uses Slack's own `mrkdwn` convention (backticks for
  monospace, `:warning:` for an emoji) - the one adapter in the project
  where the destination has its own formatting worth using. Neither
  `LogStubNotificationPort`'s plain-text log line nor
  `ConsoleMetricsPublisher`'s key=value output renders markup, so neither
  uses any. The formatting choice follows the destination, not a project
  convention applied everywhere.
- `slack_sdk` gets its own `slack` extra even though
  `slack_notification_port.py` itself never imports it - it's what
  whoever builds the real `client` will need, same reasoning as every
  extra since [09](09-·-SklearnModelInference-adapter).
- After this PR, `NotificationPort` and `MetricsPublisher` are both fully
  covered, alongside `FileStorage` and `DatasetRepository`. Only
  `ModelInferencePort`'s Vertex AI side is still missing.

## Why it matters for the rest of the project

This page confirms [14](14-·-CloudMonitoringMetricsPublisher-adapter) was
a genuine exception, not the start of a new pattern - most real adapters
in this project duck-type one plain method, and this is the last proof of
that before [16](16-·-VertexAiModelInference-adapter) closes out the
remaining port.

Back to [Home](Home) · Previous: [14 · CloudMonitoringMetricsPublisher adapter](14-·-CloudMonitoringMetricsPublisher-adapter) · Next: [16 · VertexAiModelInference adapter](16-·-VertexAiModelInference-adapter)
