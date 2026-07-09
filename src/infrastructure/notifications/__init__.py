"""Notification adapters implementing the NotificationPort (Slack/email, log stub)."""

from src.infrastructure.notifications.log_stub_notification_port import (
    LogStubNotificationPort,
)

__all__ = ["LogStubNotificationPort"]
