"""ModelInferencePort.

Runs a model against a dataset that has already passed validation.
Adapters implement this against a local scikit-learn model or a Vertex
AI endpoint, so the same pipeline can run inference locally during
development and against a deployed model in production, without the
use case that calls this port knowing which one it is talking to.

Unlike the other four ports, this one is optional in the pipeline: the
use case only calls it if the dataset was accepted by the quality rule.
A dataset that fails validation never reaches a model.
"""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class ModelInferencePort(ABC):
    """Abstract contract for running inference on a validated dataset."""

    @abstractmethod
    def predict(
        self, dataset_name: str, rows: Sequence[Mapping[str, Any]]
    ) -> Sequence[Any]:
        """Return one prediction per row in rows.

        dataset_name is passed the same way it is to DatasetRepository
        and MetricsPublisher, so an adapter that needs to pick a model
        or an endpoint based on which dataset it is looking at (a
        Vertex AI adapter routing to a different endpoint per dataset,
        for example) has that information without the use case needing
        a separate method or a different call convention.

        The return type is deliberately generic: a prediction could be
        a class label, a probability, or something else entirely,
        depending on the model, this port does not assume which.
        """
        raise NotImplementedError
