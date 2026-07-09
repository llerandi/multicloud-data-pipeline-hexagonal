"""MetricsPublisher port.

Publishes the quality metrics produced by a validation run. Adapters
implement this against Cloud Monitoring or, for local development, a
version that just prints to the console.
"""

from abc import ABC, abstractmethod

from src.domain.models import DataQualityReport


class MetricsPublisher(ABC):
    """Abstract contract for publishing a DataQualityReport."""

    @abstractmethod
    def publish(self, dataset_name: str, report: DataQualityReport) -> None:
        """Send the metrics in report somewhere they can be observed.

        report is a domain object, not a dict, so an adapter always
        gets the same well-defined fields (null_ratio and friends)
        regardless of which monitoring backend it talks to.
        """
        raise NotImplementedError
