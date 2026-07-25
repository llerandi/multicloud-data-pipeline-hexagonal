"""SlackNotificationPort: a NotificationPort adapter backed by Slack.

Back to the same pattern as most adapters before CloudMonitoringMetricsPublisher:
sending a Slack message, whether through an incoming webhook or the
slack_sdk Web API client, comes down to one call that takes a plain
string. This module does not import slack_sdk, or make any HTTP request
itself, it only calls .send(message) on whatever client object it is
given.
"""

from typing import Any

from src.application.ports import NotificationPort


class SlackNotificationPort(NotificationPort):
    """Sends a failure notification to Slack using a caller-supplied client.

    client is expected to already be configured, whether that means a
    slack_sdk WebClient authenticated with a bot token, or a thin
    wrapper around an incoming webhook URL, and to expose one method,
    send(message). Same role a connection plays for
    PostgresDatasetRepository: a ready-to-use collaborator, this
    adapter does not authenticate to Slack or know which channel or
    webhook to use, that is configured wherever the real client gets
    built.
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    def notify_failure(self, dataset_name: str, reason: str) -> None:
        """Send a message describing why dataset_name was rejected.

        Formatted using Slack's own lightweight markup (mrkdwn):
        backticks for the dataset name, a warning emoji shortcode at
        the front. Neither LogStubNotificationPort's plain %s message
        nor ConsoleMetricsPublisher's key=value line use any markup,
        because neither a log aggregator nor a terminal renders it,
        Slack does, so this is the one adapter in the project where
        formatting the message for its destination's own conventions
        actually matters.
        """
        message = f":warning: dataset `{dataset_name}` rejected: {reason}"
        self._client.send(message)
