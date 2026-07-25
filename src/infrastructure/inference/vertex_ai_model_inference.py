"""VertexAiModelInference: a ModelInferencePort adapter backed by a
deployed Vertex AI endpoint.

Same reasoning as most adapters in this project: this module does not
import google-cloud-aiplatform at all. It only calls
.predict(endpoint, instances) on whatever client object it is given,
and reads .predictions off the result, the one method and attribute any
object shaped like Vertex AI's real PredictionServiceClient exposes for
online prediction.
"""

from typing import Any, Mapping, Sequence

from src.application.ports import ModelInferencePort


class VertexAiModelInference(ModelInferencePort):
    """Runs predict() against a deployed Vertex AI endpoint.

    client is expected to already be authenticated against a specific
    GCP project and region, built by whoever constructs this class,
    same role a connection plays for PostgresDatasetRepository. endpoint
    is the fully qualified endpoint resource name Vertex AI expects,
    for example "projects/.../locations/.../endpoints/...".

    feature_names is the set of keys read from each row to build the
    instance sent for prediction, same purpose as
    SklearnModelInference's feature_names, but a different requirement
    underneath: a deployed Vertex AI model expects each instance as a
    named JSON object, {"age": 30, "income": 50000}, matching whatever
    keys its serving signature was built with, not a positional array
    with no names attached the way scikit-learn wants. Order does not
    matter here the way it does for the local adapter, which keys are
    present does.
    """

    def __init__(
        self, client: Any, endpoint: str, feature_names: Sequence[str]
    ) -> None:
        self._client = client
        self._endpoint = endpoint
        self._feature_names = feature_names

    def predict(
        self, dataset_name: str, rows: Sequence[Mapping[str, Any]]
    ) -> Sequence[Any]:
        instances = [
            {name: row[name] for name in self._feature_names} for row in rows
        ]
        response = self._client.predict(endpoint=self._endpoint, instances=instances)

        # Wrapped in list() for the same reason SklearnModelInference
        # converts a numpy array: ModelInferencePort promises a plain
        # Sequence back, regardless of what type the real client
        # happens to return its predictions as.
        return list(response.predictions)
