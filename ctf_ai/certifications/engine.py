"""
Motor de Quizzes y Simulacros de Examen para Certificaciones de Ciberseguridad.
Orquesta sesiones interactivas, validación de respuestas, retroalimentación pedagógica,
evaluación por dominios oficiales y generación híbrida asistida por IA.
"""

import json
import random
import re
from typing import Any, Dict, List, Optional

from ctf_ai.ai_providers import AIRouter
from ctf_ai.certifications.catalog import (
    CERTIFICATION_CATALOG,
    CertificationInfo,
    get_cert_by_name_or_alias,
)
from ctf_ai.certifications.questions import CERT_QUESTION_BANK


class CertificationQuizEngine:
    """Motor de evaluación y simulacros de examen para certificaciones de ciberseguridad."""

    def __init__(self, ai_router: Optional[AIRouter] = None):
        self.router = ai_router
        self.current_cert: Optional[CertificationInfo] = None
        self.questions: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self.user_answers: List[Dict[str, Any]] = []
        self.is_active: bool = False

    def start_quiz(
        self,
        cert_identifier: str,
        num_questions: int = 5,
        domain_filter: Optional[str] = None,
        use_ai: bool = True,
    ) -> CertificationInfo:
        """
        Inicia una sesión de examen/quiz para una certificación específica.
        Resuelve la certificación por id, alias o número.
        """
        cert = get_cert_by_name_or_alias(cert_identifier)
        if not cert:
            # Fallback por defecto a ISC2 CC si no coincide
            cert = CERTIFICATION_CATALOG["isc2_cc"]

        self.current_cert = cert
        self.current_index = 0
        self.user_answers = []
        self.is_active = True

        # Obtener preguntas curadas del banco offline
        offline_candidates = [
            q for q in CERT_QUESTION_BANK
            if q.get("cert_id") == cert.cert_id
        ]

        if domain_filter:
            filt_lower = domain_filter.lower()
            filtered = [
                q for q in offline_candidates
                if filt_lower in q.get("domain", "").lower()
            ]
            if filtered:
                offline_candidates = filtered

        # Mezclar preguntas offline
        selected_questions = list(offline_candidates)
        random.shuffle(selected_questions)

        # Si hay pocas preguntas locales y tenemos IA, intentar generar adicionales
        needed = max(1, num_questions)
        if len(selected_questions) < needed and use_ai and self.router:
            ai_generated = self._generate_ai_questions(
                cert=cert,
                count=needed - len(selected_questions),
                domain=domain_filter,
            )
            selected_questions.extend(ai_generated)

        # Si aún no llegamos a la cantidad pedida, re-muestrear del banco offline
        if selected_questions and len(selected_questions) < needed:
            while len(selected_questions) < needed:
                selected_questions.append(random.choice(offline_candidates or CERT_QUESTION_BANK))

        self.questions = selected_questions[:needed]
        return self.current_cert

    def explain_concept_step(
        self,
        cert: Any,
        topic: Any,
        step: Any,
        use_ai: bool = True,
    ) -> str:
        """Explica el concepto del paso poco a poco de forma didáctica usando IA o lección curada."""
        if use_ai and self.router:
            prompt = f"""Eres el Mentor de Ciberseguridad de CTF-AI.
Explica al alumno de forma clara, didáctica, amena y paso a paso el siguiente concepto clave de la certificación '{cert.name}' (Dominio: {topic.domain}):

CONCEPTO: '{step.concept_title}'
BASE TEMÁTICA: {step.explanation}

REGLAS PEDAGÓGICAS:
1. Explica paso a paso con lenguaje directo, didáctico y profesional en español.
2. Incluye una analogía clara o caso real del mundo de la seguridad (auditoría, incidentes, pentest).
3. Explica el porqué técnico y cómo previene brechas de seguridad.
4. Mantén la explicación concisa, visual y motivadora (máximo 3 párrafos).
5. NO reveles preguntas de examen ni respuestas en este paso."""
            try:
                resp = self.router.ask(prompt=prompt)
                if resp and len(resp.strip()) > 50:
                    return resp.strip()
            except Exception:
                pass
        return step.explanation

    def get_concept_check(self, cert: Any, topic: Any, step: Any, step_index: int, total_steps: int) -> Dict[str, Any]:
        """Prepara los datos de la pregunta de comprobación inmediata del concepto."""
        q = dict(step.check_question)
        q["index"] = step_index + 1
        q["total"] = total_steps
        q["cert_name"] = cert.name if hasattr(cert, "name") else "Certificación"
        q["domain"] = topic.domain if hasattr(topic, "domain") else "General"
        q["concept_title"] = step.concept_title
        return q

    def start_difficult_module_exam(
        self,
        cert_identifier: str,
        module_index: int,
        num_questions: int = 5,
        use_ai: bool = True,
    ) -> CertificationInfo:
        """Inicia el Examen Difícil del Módulo cuando el alumno domina todos los conceptos."""
        cert = get_cert_by_name_or_alias(cert_identifier) or CERTIFICATION_CATALOG["isc2_cc"]
        self.current_cert = cert
        self.current_index = 0
        self.user_answers = []
        self.is_active = True
        self.is_final_exam = False

        topic = None
        if 0 <= module_index < len(cert.study_topics):
            topic = cert.study_topics[module_index]

        diff_questions = []
        if topic:
            diff_questions = list(topic.get_difficult_exam_questions(count=num_questions))

        # Si aún faltan, complementar con preguntas del banco offline de este dominio
        if len(diff_questions) < num_questions:
            dom = topic.domain if topic else ""
            offline_matching = [
                q for q in CERT_QUESTION_BANK
                if q.get("cert_id") == cert.cert_id and dom.lower() in q.get("domain", "").lower()
            ]
            for q in offline_matching:
                if q not in diff_questions and len(diff_questions) < num_questions:
                    diff_questions.append(q)

        # Si todavía faltan, intentar generar con IA o completar
        needed = max(1, num_questions)
        if len(diff_questions) < needed and use_ai and self.router and topic:
            ai_gen = self._generate_ai_questions(cert=cert, count=needed - len(diff_questions), domain=topic.domain)
            diff_questions.extend(ai_gen)

        while len(diff_questions) < needed:
            diff_questions.append(random.choice(CERT_QUESTION_BANK))

        self.questions = diff_questions[:needed]
        return self.current_cert

    def start_module_quiz(
        self,
        cert_identifier: str,
        module_index: int,
        num_questions: int = 3,
        use_ai: bool = True,
    ) -> CertificationInfo:
        """Inicia un mini-quiz de validación de competencias para un módulo específico."""
        return self.start_difficult_module_exam(
            cert_identifier=cert_identifier,
            module_index=module_index,
            num_questions=num_questions,
            use_ai=use_ai,
        )

    def start_final_exam(
        self,
        cert_identifier: str,
        num_questions: int = 100,
        use_ai: bool = True,
        resume_from: Optional[Dict[str, Any]] = None,
    ) -> CertificationInfo:
        """
        Inicia el Gran Examen Final Comprensivo (100 preguntas) que abarca todos
        los dominios oficiales de la certificación tras completar todos los módulos.
        Soporta reanudación si había un examen pausado.
        """
        cert = get_cert_by_name_or_alias(cert_identifier) or CERTIFICATION_CATALOG["isc2_cc"]
        self.current_cert = cert
        self.is_final_exam = True

        if resume_from and resume_from.get("questions"):
            self.questions = resume_from["questions"]
            self.current_index = resume_from.get("current_index", 0)
            self.user_answers = resume_from.get("user_answers", [])
            self.is_active = True
            return self.current_cert

        self.current_index = 0
        self.user_answers = []
        self.is_active = True

        # Reunir preguntas ponderadas por dominio
        exam_questions = []
        for topic in cert.study_topics:
            exam_questions.extend(topic.get_difficult_exam_questions(count=10))

        cert_bank = [q for q in CERT_QUESTION_BANK if q.get("cert_id") == cert.cert_id]
        exam_questions.extend(cert_bank)

        # Eliminar duplicados
        unique_questions = []
        seen = set()
        for q in exam_questions:
            key = q.get("question", "")
            if key and key not in seen:
                seen.add(key)
                unique_questions.append(q)

        needed = max(5, num_questions)
        random.shuffle(unique_questions)
        selected = list(unique_questions)

        if len(selected) < needed:
            sample_pool = unique_questions if unique_questions else CERT_QUESTION_BANK
            while len(selected) < needed:
                for base_q in sample_pool:
                    if len(selected) >= needed:
                        break
                    var_q = dict(base_q)
                    var_q["question_id"] = f"var_{len(selected)+1}"
                    selected.append(var_q)

        self.questions = selected[:needed]
        return self.current_cert

    def get_exam_state(self) -> Dict[str, Any]:
        """Retorna el estado actual de la sesión de examen para guardado/pausa."""
        return {
            "cert_id": self.current_cert.cert_id if self.current_cert else "",
            "current_index": self.current_index,
            "total_questions": len(self.questions),
            "questions": self.questions,
            "user_answers": self.user_answers,
            "is_final_exam": getattr(self, "is_final_exam", False),
        }

    def has_next_question(self) -> bool:
        """Indica si quedan preguntas pendientes por responder en la sesión activa."""
        return self.is_active and self.current_index < len(self.questions)

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de la pregunta activa actual sin desvelar la respuesta."""
        if not self.has_next_question():
            return None
        q = self.questions[self.current_index]
        return {
            "index": self.current_index + 1,
            "total": len(self.questions),
            "cert_name": self.current_cert.name if self.current_cert else "Certificación",
            "cert_id": self.current_cert.cert_id if self.current_cert else "",
            "domain": q.get("domain", "General"),
            "scenario": q.get("scenario", ""),
            "question": q.get("question", ""),
            "options": q.get("options", []),
        }

    def submit_answer(self, raw_user_answer: str) -> Dict[str, Any]:
        """
        Evalúa la respuesta del alumno para la pregunta actual y avanza el índice.
        Acepta 'A', 'B', 'C', 'D' (o 'a)', etc.).
        """
        if not self.has_next_question():
            return {"error": "No hay ninguna pregunta activa en la sesión."}

        q = self.questions[self.current_index]
        correct_answer = q.get("answer", "A").strip().upper()

        # Extraer la letra elegida por el usuario
        cleaned = raw_user_answer.strip().upper()
        match = re.search(r"([A-D])", cleaned)
        user_choice = match.group(1) if match else cleaned[:1]

        is_correct = (user_choice == correct_answer)

        record = {
            "question_index": self.current_index + 1,
            "domain": q.get("domain", "General"),
            "question": q.get("question", ""),
            "scenario": q.get("scenario", ""),
            "user_choice": user_choice,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "Sin explicación disponible."),
        }
        self.user_answers.append(record)
        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.is_active = False

        return record

    def get_scorecard(self) -> Dict[str, Any]:
        """
        Calcula el diagnóstico de desempeño final:
        Porcentaje, estatus de Aprobado/No Aprobado según el umbral oficial de la certificación,
        y desglose analítico de dominios fuertes y áreas a reforzar.
        """
        total = len(self.user_answers)
        if total == 0:
            return {
                "total": 0,
                "correct": 0,
                "percentage": 0.0,
                "passed": False,
                "cert_name": self.current_cert.name if self.current_cert else "General",
                "domain_breakdown": {},
                "weak_domains": [],
                "strong_domains": [],
                "recommendations": [],
            }

        correct_count = sum(1 for a in self.user_answers if a["is_correct"])
        percentage = round((correct_count / total) * 100, 1)

        passing_threshold = self.current_cert.passing_percentage if self.current_cert else 70.0
        passed = percentage >= passing_threshold

        # Desglose por dominios
        domain_stats: Dict[str, Dict[str, int]] = {}
        for a in self.user_answers:
            dom = a["domain"]
            if dom not in domain_stats:
                domain_stats[dom] = {"total": 0, "correct": 0}
            domain_stats[dom]["total"] += 1
            if a["is_correct"]:
                domain_stats[dom]["correct"] += 1

        domain_breakdown: Dict[str, Dict[str, Any]] = {}
        weak_domains: List[str] = []
        strong_domains: List[str] = []

        for dom, stats in domain_stats.items():
            pct = round((stats["correct"] / stats["total"]) * 100, 1) if stats["total"] > 0 else 0.0
            domain_breakdown[dom] = {
                "total": stats["total"],
                "correct": stats["correct"],
                "percentage": pct,
                "status": "Dominado" if pct >= passing_threshold else "Reforzar",
            }
            if pct < passing_threshold:
                weak_domains.append(dom)
            else:
                strong_domains.append(dom)

        # Generar recomendaciones de estudio
        recommendations: List[str] = []
        if self.current_cert and weak_domains:
            for topic in self.current_cert.study_topics:
                for w in weak_domains:
                    if w.lower() in topic.domain.lower() or topic.domain.lower() in w.lower():
                        recommendations.append(
                            f"Repasar '{topic.title}' en {topic.domain}: conceptos de {', '.join(topic.concepts[:2])}"
                        )
                        break

        if not recommendations and not passed:
            recommendations.append("Revisa las explicaciones de las preguntas falladas y realiza un nuevo simulacro.")

        return {
            "cert_id": self.current_cert.cert_id if self.current_cert else "",
            "cert_name": self.current_cert.name if self.current_cert else "Certificación",
            "vendor": self.current_cert.vendor if self.current_cert else "",
            "passing_score": self.current_cert.passing_score if self.current_cert else "70%",
            "passing_percentage": passing_threshold,
            "total": total,
            "correct": correct_count,
            "percentage": percentage,
            "passed": passed,
            "is_final_exam": getattr(self, "is_final_exam", False),
            "domain_breakdown": domain_breakdown,
            "weak_domains": weak_domains,
            "strong_domains": strong_domains,
            "recommendations": recommendations,
        }

    def _generate_ai_questions(
        self,
        cert: CertificationInfo,
        count: int = 2,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Genera preguntas adicionales dinámicas utilizando el enrutador de IA."""
        if not self.router:
            return []

        target_domain = domain or (random.choice(cert.domains)["name"] if cert.domains else "General")
        prompt = f"""Eres un creador oficial de exámenes para la certificación '{cert.name}' de {cert.vendor}.
Genera exactamente {count} preguntas de práctica de opción múltiple (A, B, C, D) basadas en un escenario realista para el dominio: '{target_domain}'.

REGLAS DE FORMATO ESTRICTAS:
Responde ÚNICAMENTE con un arreglo JSON válido (sin markdown adicional fuera del bloque JSON) con la siguiente estructura por objeto:
[
  {{
    "cert_id": "{cert.cert_id}",
    "domain": "{target_domain}",
    "scenario": "Escenario técnico realista en el trabajo...",
    "question": "¿Cuál es la acción o concepto correcto...?",
    "options": [
      "A) Opción 1",
      "B) Opción 2",
      "C) Opción 3",
      "D) Opción 4"
    ],
    "answer": "A",
    "explanation": "Explicación detallada de por qué A es correcta y las demás son incorrectas."
  }}
]
"""
        try:
            raw = self.router.ask(prompt=prompt)
            json_match = re.search(r"\[\s*\{.*\}\s*\]", raw, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if isinstance(parsed, list):
                    return parsed
        except Exception:
            pass

        return []
