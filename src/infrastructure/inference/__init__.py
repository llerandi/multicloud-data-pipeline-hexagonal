"""Inference adapters implementing the ModelInferencePort (local scikit-learn, Vertex AI)."""

from src.infrastructure.inference.sklearn_model_inference import SklearnModelInference
from src.infrastructure.inference.vertex_ai_model_inference import (
    VertexAiModelInference,
)

__all__ = ["SklearnModelInference", "VertexAiModelInference"]
