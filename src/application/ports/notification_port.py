"""NotificationPort.

Tells someone that a dataset failed validation. Adapters implement
this against Slack, email, or a stub that only logs, so the pipeline
behaves the same in tests and in production except for where the
message ends up.
"""

from abc import ABC, abstractmethod


class NotificationPort(ABC):
    """Abstract contract for reporting a validation failure."""

    @abstractmethod
    def notify_failure(self, dataset_name: str, reason: str) -> None:
        """Report that dataset_name failed with reason.

        reason is a plain string rather than the DatasetRejectedError
        itself, so this port does not need to import domain
        exceptions, the use case is responsible for turning an
        exception into a message worth reading.
        """
        raise NotImplementedError
