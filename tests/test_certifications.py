"""
Pruebas Unitarias para el Módulo de Certificaciones de Ciberseguridad y Motor de Quizzes.
Valida la integridad del catálogo oficial, resolución por alias, consistencia del banco
de preguntas, lógica de puntuación del simulacro, evaluación de dominios y métodos de UI.
"""

import unittest
from io import StringIO
from rich.console import Console

from ctf_ai.certifications.catalog import (
    CERTIFICATION_CATALOG,
    CertificationInfo,
    StudyTopic,
    get_cert_by_name_or_alias,
    list_all_certifications,
)
from ctf_ai.certifications.questions import CERT_QUESTION_BANK
from ctf_ai.certifications.engine import CertificationQuizEngine
from ctf_ai.ui import CTFInterface


class TestCertificationCatalog(unittest.TestCase):
    """Pruebas de integridad del catálogo oficial de certificaciones."""

    def test_catalog_contains_key_certifications(self):
        expected_keys = [
            "isc2_cc",
            "comptia_secplus",
            "comptia_netplus",
            "ejpt",
            "cjca",
            "pjpt",
            "btl1",
            "ceh",
        ]
        for key in expected_keys:
            self.assertIn(key, CERTIFICATION_CATALOG, f"La certificación '{key}' debe estar en el catálogo.")

    def test_certification_fields_integrity(self):
        all_certs = list_all_certifications()
        self.assertGreaterEqual(len(all_certs), 8)

        for cert in all_certs:
            self.assertTrue(cert.cert_id, "cert_id no debe estar vacío")
            self.assertTrue(cert.name, "name no debe estar vacío")
            self.assertTrue(cert.vendor, "vendor no debe estar vacío")
            self.assertTrue(cert.level, "level no debe estar vacío")
            self.assertTrue(cert.exam_format, "exam_format no debe estar vacío")
            self.assertTrue(cert.passing_score, "passing_score no debe estar vacío")
            self.assertGreater(cert.passing_percentage, 0.0, "passing_percentage debe ser > 0")
            self.assertGreater(len(cert.domains), 0, f"'{cert.cert_id}' debe tener dominios oficiales")
            self.assertGreater(len(cert.study_topics), 0, f"'{cert.cert_id}' debe tener temas de estudio")
            self.assertTrue(cert.official_url.startswith("http"), "official_url debe ser HTTP/HTTPS válido")

            # Validar estructura de study_topics
            for topic in cert.study_topics:
                self.assertTrue(topic.domain)
                self.assertTrue(topic.title)
                self.assertGreater(len(topic.concepts), 0)
                self.assertIsInstance(topic.exam_tips, list)
                self.assertIsInstance(topic.recommended_labs, list)

            # Validar to_dict()
            c_dict = cert.to_dict()
            self.assertEqual(c_dict["cert_id"], cert.cert_id)
            self.assertEqual(len(c_dict["study_topics"]), len(cert.study_topics))

    def test_resolution_by_alias_and_number(self):
        # Resolución numérica
        c1 = get_cert_by_name_or_alias("1")
        self.assertIsNotNone(c1)
        self.assertEqual(c1.cert_id, "isc2_cc")

        # Resolución por alias directos
        self.assertEqual(get_cert_by_name_or_alias("isc2").cert_id, "isc2_cc")
        self.assertEqual(get_cert_by_name_or_alias("cc").cert_id, "isc2_cc")
        self.assertEqual(get_cert_by_name_or_alias("sec+").cert_id, "comptia_secplus")
        self.assertEqual(get_cert_by_name_or_alias("security+").cert_id, "comptia_secplus")
        self.assertEqual(get_cert_by_name_or_alias("net+").cert_id, "comptia_netplus")
        self.assertEqual(get_cert_by_name_or_alias("ejpt").cert_id, "ejpt")
        self.assertEqual(get_cert_by_name_or_alias("cjca").cert_id, "cjca")
        self.assertEqual(get_cert_by_name_or_alias("pjpt").cert_id, "pjpt")
        self.assertEqual(get_cert_by_name_or_alias("btl1").cert_id, "btl1")
        self.assertEqual(get_cert_by_name_or_alias("ceh").cert_id, "ceh")

        # Tolerancia a mayúsculas y espacios
        self.assertEqual(get_cert_by_name_or_alias("  SEC+  ").cert_id, "comptia_secplus")
        self.assertEqual(get_cert_by_name_or_alias("EJPT").cert_id, "ejpt")

        # Búsqueda inválida devuelve None
        self.assertIsNone(get_cert_by_name_or_alias("cert_inexistente_999"))
        self.assertIsNone(get_cert_by_name_or_alias(""))


class TestQuestionBank(unittest.TestCase):
    """Pruebas de integridad del banco de preguntas curadas de examen."""

    def test_questions_structure_and_answers(self):
        self.assertGreaterEqual(len(CERT_QUESTION_BANK), 12)

        valid_answers = {"A", "B", "C", "D"}
        for idx, q in enumerate(CERT_QUESTION_BANK):
            self.assertIn("cert_id", q, f"Pregunta #{idx} debe tener cert_id")
            self.assertIn("domain", q, f"Pregunta #{idx} debe tener domain")
            self.assertIn("question", q, f"Pregunta #{idx} debe tener question")
            self.assertIn("options", q, f"Pregunta #{idx} debe tener options")
            self.assertIn("answer", q, f"Pregunta #{idx} debe tener answer")
            self.assertIn("explanation", q, f"Pregunta #{idx} debe tener explanation")

            options = q["options"]
            self.assertEqual(len(options), 4, f"Pregunta #{idx} debe tener exactamente 4 opciones")
            self.assertIn(q["answer"], valid_answers, f"Pregunta #{idx} answer debe ser A, B, C o D")
            self.assertGreater(len(q["explanation"]), 15, f"Pregunta #{idx} debe tener explicación pedagógica")


class TestCertificationQuizEngine(unittest.TestCase):
    """Pruebas del motor interactivo de quizzes y evaluación."""

    def setUp(self):
        self.engine = CertificationQuizEngine(ai_router=None)

    def test_start_quiz_session(self):
        cert = self.engine.start_quiz("isc2", num_questions=3, use_ai=False)
        self.assertEqual(cert.cert_id, "isc2_cc")
        self.assertTrue(self.engine.is_active)
        self.assertEqual(len(self.engine.questions), 3)
        self.assertTrue(self.engine.has_next_question())

    def test_quiz_answering_and_scorecard(self):
        self.engine.start_quiz("isc2", num_questions=2, use_ai=False)

        q1 = self.engine.get_current_question()
        self.assertIsNotNone(q1)
        self.assertEqual(q1["index"], 1)
        self.assertEqual(q1["total"], 2)
        # Asegurar que la respuesta correcta no se filtra en los datos públicos de la pregunta
        self.assertNotIn("answer", q1)

        # Responder correctamente la primera pregunta
        actual_q1 = self.engine.questions[0]
        correct_letter = actual_q1["answer"]
        res1 = self.engine.submit_answer(correct_letter)
        self.assertTrue(res1["is_correct"])
        self.assertEqual(res1["user_choice"], correct_letter)

        # Responder erróneamente la segunda pregunta
        actual_q2 = self.engine.questions[1]
        wrong_letter = "D" if actual_q2["answer"] != "D" else "A"
        res2 = self.engine.submit_answer(wrong_letter)
        self.assertFalse(res2["is_correct"])

        # Verificar que la sesión finalizó
        self.assertFalse(self.engine.has_next_question())
        self.assertFalse(self.engine.is_active)

        # Verificar scorecard
        scorecard = self.engine.get_scorecard()
        self.assertEqual(scorecard["total"], 2)
        self.assertEqual(scorecard["correct"], 1)
        self.assertEqual(scorecard["percentage"], 50.0)
        self.assertFalse(scorecard["passed"], "50% no debe superar el umbral de 70% de ISC2 CC")
        self.assertGreater(len(scorecard["domain_breakdown"]), 0)

    def test_perfect_score_passes_exam(self):
        self.engine.start_quiz("sec+", num_questions=2, use_ai=False)

        for _ in range(2):
            curr = self.engine.questions[self.engine.current_index]
            self.engine.submit_answer(curr["answer"])

        scorecard = self.engine.get_scorecard()
        self.assertEqual(scorecard["correct"], 2)
        self.assertEqual(scorecard["percentage"], 100.0)
        self.assertTrue(scorecard["passed"], "100% debe aprobar")
        self.assertGreaterEqual(len(scorecard["strong_domains"]), 1)


class TestUIIntegration(unittest.TestCase):
    """Verifica que los métodos de presentación visual en Rich ejecuten sin errores de sintaxis o renderizado."""

    def setUp(self):
        self.string_io = StringIO()
        self.console = Console(file=self.string_io, color_system=None, width=120)
        self.ui = CTFInterface(console=self.console)

    def test_ui_display_methods(self):
        all_certs = list_all_certifications()
        # 1. Menú de certificaciones
        self.ui.display_certifications_menu(all_certs)

        # 2. Temas de estudio
        self.ui.display_cert_study_topics(all_certs[0])

        # 3. Pregunta de quiz
        sample_q = {
            "index": 1,
            "total": 5,
            "cert_name": "ISC2 CC",
            "domain": "Domain 1: Security Principles",
            "scenario": "Escenario de prueba en laboratorio.",
            "question": "¿Cuál es el pilar de la integridad?",
            "options": ["A) Opción A", "B) Opción B", "C) Opción C", "D) Opción D"],
        }
        self.ui.display_cert_quiz_question(sample_q)

        # 4. Feedback
        self.ui.display_quiz_feedback({
            "is_correct": True,
            "user_choice": "A",
            "correct_answer": "A",
            "explanation": "Explicación correcta.",
        })
        self.ui.display_quiz_feedback({
            "is_correct": False,
            "user_choice": "B",
            "correct_answer": "A",
            "explanation": "Explicación de fallo.",
        })

        # 5. Scorecard
        scorecard = {
            "cert_name": "ISC2 CC",
            "vendor": "ISC2",
            "total": 5,
            "correct": 4,
            "percentage": 80.0,
            "passing_percentage": 70.0,
            "passing_score": "700 / 1000",
            "passed": True,
            "domain_breakdown": {
                "Domain 1: Security Principles": {"total": 5, "correct": 4, "percentage": 80.0, "status": "Dominado"}
            },
            "recommendations": ["Sigue practicando con laboratorios."],
        }
        self.ui.display_cert_scorecard(scorecard)

        output = self.string_io.getvalue()
        self.assertIn("Catálogo de Certificaciones", output)
        self.assertIn("PLAN DE PREPARACIÓN OFICIAL", output)
        self.assertIn("EVALUACIÓN", output)
        self.assertIn("RESULTADO DEL SIMULACRO", output)


class TestCertificationProgress(unittest.TestCase):
    """Pruebas de persistencia local del progreso en la máquina del usuario."""

    def setUp(self):
        import tempfile
        from pathlib import Path
        self.temp_dir = tempfile.TemporaryDirectory()
        self.progress_file = Path(self.temp_dir.name) / "test_cert_progress.json"
        from ctf_ai.certifications.progress import CertificationProgressTracker
        self.tracker = CertificationProgressTracker(file_path=self.progress_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_progress_persistence_and_module_unlocking(self):
        cert_id = "isc2_cc"
        total_modules = 5

        # 1. Comprobar estado inicial
        prog = self.tracker.get_cert_progress(cert_id, total_modules=total_modules)
        self.assertEqual(prog["current_module_index"], 0)
        self.assertEqual(len(prog["completed_modules"]), 0)
        self.assertFalse(prog["all_modules_completed"])
        self.assertFalse(prog["final_exam_unlocked"])

        # 2. Superar Módulo 1 (índice 0)
        self.tracker.mark_module_completed(cert_id, module_index=0, score=3, total=3, total_modules=total_modules)
        prog = self.tracker.get_cert_progress(cert_id, total_modules=total_modules)
        self.assertEqual(prog["current_module_index"], 1)
        self.assertIn(0, prog["completed_modules"])
        self.assertEqual(prog["completion_percentage"], 20.0)
        self.assertFalse(prog["all_modules_completed"])

        # 3. Superar módulos restantes 1..4
        for m in range(1, total_modules):
            self.tracker.mark_module_completed(cert_id, module_index=m, score=3, total=3, total_modules=total_modules)

        prog = self.tracker.get_cert_progress(cert_id, total_modules=total_modules)
        self.assertEqual(len(prog["completed_modules"]), total_modules)
        self.assertEqual(prog["completion_percentage"], 100.0)
        self.assertTrue(prog["all_modules_completed"])
        self.assertTrue(prog["final_exam_unlocked"])

        # 4. Simular apagado de máquina: crear nueva instancia recargando desde disco
        from ctf_ai.certifications.progress import CertificationProgressTracker
        reloaded_tracker = CertificationProgressTracker(file_path=self.progress_file)
        reloaded_prog = reloaded_tracker.get_cert_progress(cert_id, total_modules=total_modules)
        self.assertEqual(reloaded_prog["completion_percentage"], 100.0)
        self.assertTrue(reloaded_prog["all_modules_completed"])
        self.assertTrue(reloaded_prog["final_exam_unlocked"])

        # 5. Registrar Gran Examen Final
        attempt = reloaded_tracker.record_final_exam(cert_id, score=90, total=100, percentage=90.0, passed=True)
        self.assertTrue(attempt["passed"])
        self.assertEqual(len(reloaded_prog["final_exam_results"]), 1)

    def test_step_progress_persistence_and_pause(self):
        cert_id = "isc2_cc"
        # Marcar paso 0 y 1 como completados
        self.tracker.mark_step_completed(cert_id, module_index=0, step_index=0, total_steps=5)
        step_data = self.tracker.get_step_progress(cert_id, module_index=0)
        self.assertEqual(step_data["current_step_index"], 1)
        self.assertIn(0, step_data["completed_steps"])

        self.tracker.mark_step_completed(cert_id, module_index=0, step_index=1, total_steps=5)
        step_data = self.tracker.get_step_progress(cert_id, module_index=0)
        self.assertEqual(step_data["current_step_index"], 2)

        # Probar guardado de examen pausado
        exam_state = {"current_index": 45, "total_questions": 100, "questions": [{"q": 1}]}
        self.tracker.save_paused_exam(cert_id, exam_state)
        paused = self.tracker.get_paused_exam(cert_id)
        self.assertIsNotNone(paused)
        self.assertEqual(paused["current_index"], 45)

        # Limpiar examen pausado
        self.tracker.clear_paused_exam(cert_id)
        self.assertIsNone(self.tracker.get_paused_exam(cert_id))


class TestModuleQuizAndFinalExamEngine(unittest.TestCase):
    """Pruebas del motor para quizzes de módulo y Gran Examen Final."""

    def setUp(self):
        self.engine = CertificationQuizEngine(ai_router=None)

    def test_start_module_quiz(self):
        cert = self.engine.start_module_quiz("isc2", module_index=0, num_questions=3, use_ai=False)
        self.assertEqual(cert.cert_id, "isc2_cc")
        self.assertEqual(len(self.engine.questions), 3)
        self.assertFalse(getattr(self.engine, "is_final_exam", False))

    def test_concept_steps_and_checks(self):
        cert = CERTIFICATION_CATALOG["isc2_cc"]
        topic = cert.study_topics[0]
        steps = topic.get_concept_steps()
        self.assertGreaterEqual(len(steps), 5)
        first_step = steps[0]
        self.assertTrue(first_step.concept_title)

        # Explicación offline
        explanation = self.engine.explain_concept_step(cert, topic, first_step, use_ai=False)
        self.assertIn("Tríada CIA", explanation)

        # Comprobación de concepto
        check = self.engine.get_concept_check(cert, topic, first_step, 0, len(steps))
        self.assertEqual(check["index"], 1)
        self.assertEqual(check["total"], len(steps))
        self.assertEqual(len(check["options"]), 4)

    def test_start_difficult_module_exam(self):
        cert = self.engine.start_difficult_module_exam("isc2_cc", module_index=0, num_questions=5, use_ai=False)
        self.assertEqual(cert.cert_id, "isc2_cc")
        self.assertEqual(len(self.engine.questions), 5)
        q = self.engine.get_current_question()
        self.assertIsNotNone(q)
        self.assertEqual(len(q["options"]), 4)

    def test_start_final_exam_100_questions(self):
        cert = self.engine.start_final_exam("sec+", num_questions=100, use_ai=False)
        self.assertEqual(cert.cert_id, "comptia_secplus")
        self.assertEqual(len(self.engine.questions), 100)
        self.assertTrue(self.engine.is_final_exam)

    def test_final_exam_resume_from_paused(self):
        paused_state = {
            "current_index": 20,
            "total_questions": 100,
            "questions": [{"question": "Pregunta 21", "options": ["A) 1", "B) 2"], "answer": "A"}],
            "user_answers": [{"q": 1}] * 20,
        }
        cert = self.engine.start_final_exam("isc2_cc", num_questions=100, use_ai=False, resume_from=paused_state)
        self.assertEqual(self.engine.current_index, 20)
        self.assertEqual(len(self.engine.user_answers), 20)


if __name__ == "__main__":
    unittest.main()

