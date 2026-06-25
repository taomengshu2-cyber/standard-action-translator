"""Standard Action Translator."""

from .diagnostician import diagnose
from .models import DiagnosisResult

__all__ = ["DiagnosisResult", "diagnose"]

__version__ = "0.1.0"
