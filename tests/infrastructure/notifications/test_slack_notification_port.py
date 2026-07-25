"""Unit tests for SlackNotificationPort.

FakeSlackClient implements just the one method this adapter calls,
send, and records what it was given. Since the adapter never imports
slack_sdk or makes an HTTP request, none of these tests need either
installed.
"""

from src.application.ports import NotificationPort
from src.infrastructure.notifications import SlackNotificationPort


class FakeSlackClient:
    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)


def test_slack_notification_port_is_a_notification_port():
    assert issubclass(SlackNotificationPort, NotificationPort)


def test_notify_failure_sends_one_message_with_dataset_name_and_reason():
    client = FakeSlackClient()
    notifier = SlackNotificationPort(client)

    notifier.notify_failure("customers", "null ratio 0.20 exceeds max 0.05")

    assert len(client.sent) == 1
    message = client.sent[0]
    assert "customers" in message
    assert "null ratio 0.20 exceeds max 0.05" in message


def test_notify_failure_formats_the_dataset_name_with_slack_markup():
    client = FakeSlackClient()
    notifier = SlackNotificationPort(client)

    notifier.notify_failure("customers", "some reason")

    message = client.sent[0]
    assert "`customers`" in message
    assert message.startswith(":warning:")
