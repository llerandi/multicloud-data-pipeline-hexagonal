"""Unit tests for VertexAiModelInference.

FakeVertexAiClient and FakeVertexAiResponse mirror the real client's
shape: predict() takes endpoint and instances as keyword arguments and
returns an object with a .predictions attribute, not a dict key, that
is how the real Vertex AI response behaves. Since the adapter never
imports google-cloud-aiplatform, none of this needs it installed.
"""

from src.application.ports import ModelInferencePort
from src.infrastructure.inference import VertexAiModelInference


class FakeVertexAiResponse:
    def __init__(self, predictions):
        self.predictions = predictions


class FakeVertexAiClient:
    def __init__(self, predictions):
        self.calls = []
        self._predictions = predictions

    def predict(self, endpoint, instances):
        self.calls.append((endpoint, instances))
        return FakeVertexAiResponse(self._predictions)


def test_vertex_ai_model_inference_is_a_model_inference_port():
    assert issubclass(VertexAiModelInference, ModelInferencePort)


def test_predict_builds_instances_as_dicts_with_only_the_selected_features():
    client = FakeVertexAiClient(predictions=[0, 1])
    inference = VertexAiModelInference(
        client=client,
        endpoint="projects/p/locations/us-central1/endpoints/1",
        feature_names=["age", "income"],
    )

    inference.predict(
        "customers",
        [
            {"income": 50000, "age": 30, "id": "1"},
            {"income": 20000, "age": 22, "id": "2"},
        ],
    )

    _, instances = client.calls[0]
    # Only the selected features are kept, order of the keys does not
    # matter the way it does for SklearnModelInference's matrix, "id"
    # is dropped because it was not in feature_names.
    assert instances == [
        {"age": 30, "income": 50000},
        {"age": 22, "income": 20000},
    ]


def test_predict_calls_the_client_with_the_configured_endpoint():
    client = FakeVertexAiClient(predictions=[1])
    inference = VertexAiModelInference(
        client=client,
        endpoint="projects/p/locations/us-central1/endpoints/1",
        feature_names=["age"],
    )

    inference.predict("customers", [{"age": 30}])

    endpoint, _ = client.calls[0]
    assert endpoint == "projects/p/locations/us-central1/endpoints/1"


def test_predict_returns_a_plain_list_of_predictions():
    client = FakeVertexAiClient(predictions=[0, 1])
    inference = VertexAiModelInference(
        client=client,
        endpoint="projects/p/locations/us-central1/endpoints/1",
        feature_names=["age"],
    )

    predictions = inference.predict("customers", [{"age": 30}, {"age": 22}])

    assert predictions == [0, 1]
    assert type(predictions) is list
