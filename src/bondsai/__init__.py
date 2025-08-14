"""BondsAI - Dual Purpose AI Assistant Package."""

from .core import DatingAssistant, Assistant
from .job_screening import JobScreeningAssistant, JobCandidate

__version__ = "1.0.0"
__all__ = ["DatingAssistant", "Assistant", "JobScreeningAssistant", "JobCandidate"]
