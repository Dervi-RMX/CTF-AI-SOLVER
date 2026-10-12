"""
Módulo de Preparación para Certificaciones de Ciberseguridad de CTF-AI Solver Pro.
Proporciona catálogos oficiales, guías temáticas de estudio, consejos de examen
y simulacros de quizzes interactivos para ISC2 CC, CompTIA Sec+, eJPT, CJCA, etc.
"""

from ctf_ai.certifications.catalog import (
    CERTIFICATION_CATALOG,
    CertificationInfo,
    StudyTopic,
    get_cert_by_name_or_alias,
    list_all_certifications,
)
from ctf_ai.certifications.questions import CERT_QUESTION_BANK
from ctf_ai.certifications.engine import CertificationQuizEngine
from ctf_ai.certifications.progress import CertificationProgressTracker, DEFAULT_PROGRESS_FILE

__all__ = [
    "CERTIFICATION_CATALOG",
    "CertificationInfo",
    "StudyTopic",
    "get_cert_by_name_or_alias",
    "list_all_certifications",
    "CERT_QUESTION_BANK",
    "CertificationQuizEngine",
    "CertificationProgressTracker",
    "DEFAULT_PROGRESS_FILE",
]
