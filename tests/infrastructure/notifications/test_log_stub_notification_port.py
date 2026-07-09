"""Unit tests for LogStubNotificationPort.

caplog is a built-in pytest fixture that captures log records emitted
during a test, the logging equivalent of capsys for stdout, so the
assertions here check what was actually logged instead of trusting that
notify_failure ran without raising.
"""

import logging

from src.application.ports import NotificationPort
from src.infrastructure.notifications import LogStubNotificationPort


def test_log_stub_notification_port_is_a_notification_port():
    assert issubclass(LogStubNotificationPort, NotificationPort)


def test_notify_failure_logs_one_warning_with_dataset_name_and_reason(caplog):
    notifier = LogStubNotificationPort()

    with caplog.at_level(logging.WARNING):
        notifier.notify_failure("customers", "null ratio 0.20 exceeds max 0.05")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "customers" in caplog.text
    assert "null ratio 0.20 exceeds max 0.05" in caplog.text


def test_notify_failure_does_not_log_below_warning_level(caplog):
    notifier = LogStubNotificationPort()

    with caplog.at_level(logging.ERROR):
        notifier.notify_failure("customers", "some reason")

    # ERROR is a stricter filter than the WARNING this adapter logs at,
    # so nothing should have been captured.
    assert caplog.records == []
