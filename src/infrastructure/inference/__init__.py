"""Inference adapters implementing the ModelInferencePort (local scikit-learn, Vertex AI)."""

from src.infrastructure.inference.sklearn_model_inference import SklearnModelInference

__all__ = ["SklearnModelInference"]
