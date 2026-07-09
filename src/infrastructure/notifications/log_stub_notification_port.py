"""LogStubNotificationPort: a NotificationPort adapter that only logs.

Meant for tests and local development, not production. It exists so the
pipeline has somewhere to send a failure notification before a real
Slack or email adapter is written. Nothing leaves the process, no
network access or credentials needed, which also makes it deterministic
enough to assert on in tests.
"""

import logging

from src.application.ports import NotificationPort

logger = logging.getLogger(__name__)


class LogStubNotificationPort(NotificationPort):
    """Logs a failure notification instead of sending it anywhere.

    Uses the standard logging module, not print, unlike
    ConsoleMetricsPublisher. The project scope describes this adapter
    as one that "only logs", as opposed to the metrics adapter, which
    is described as one that "only prints", that distinction in wording
    is kept on purpose: a rejected dataset is an event worth being able
    to filter, route to a log aggregator, or silence by level, none of
    which a bare print() call gives you.
    """

    def notify_failure(self, dataset_name: str, reason: str) -> None:
        # WARNING, not ERROR: a rejected dataset is the business rule
        # working as intended, not a bug or a crash in the pipeline
        # itself. Using %-style arguments instead of an f-string is the
        # logging module's own convention, it lets the string
        # formatting be skipped entirely if warnings are disabled.
        logger.warning("dataset %s rejected: %s", dataset_name, reason)
