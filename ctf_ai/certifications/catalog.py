"""
Catálogo de Certificaciones y Guías Temáticas de Estudio Oficiales.
Define fichas curriculares completas, dominios ponderados, criterios de aprobación,
consejos de examen y laboratorios recomendados para certificaciones de ciberseguridad.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModuleConceptStep:
    """Representa un paso o concepto atómico explicado poco a poco dentro de un módulo."""
    step_id: str
    concept_title: str
    explanation: str
    check_question: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "concept_title": self.concept_title,
            "explanation": self.explanation,
            "check_question": self.check_question,
        }


@dataclass
class StudyTopic:
    """Representa un tema o dominio clave de preparación para una certificación."""
    domain: str
    title: str
    concepts: List[str]
    exam_tips: List[str]
    recommended_labs: List[str]
    free_resources: List[Dict[str, str]] = field(default_factory=list)
    concept_steps: List[ModuleConceptStep] = field(default_factory=list)
    difficult_exam: List[Dict[str, Any]] = field(default_factory=list)

    def get_concept_steps(self) -> List[ModuleConceptStep]:
        """Obtiene la lista ordenada de pasos explicativos y comprobaciones conceptuales."""
        if self.concept_steps:
            return self.concept_steps
        steps: List[ModuleConceptStep] = []
        for i, c in enumerate(self.concepts, 1):
            parts = c.split(":", 1)
            c_title = parts[0].strip() if len(parts) > 1 else f"Concepto Clave {i}"
            c_detail = parts[1].strip() if len(parts) > 1 else c.strip()
            explanation = (
                f"En el dominio **{self.domain}**, un fundamento esencial que debes dominar es: **{c_title}**.\n\n"
                f"📌 **Fundamento técnico oficial:**\n{c_detail}\n\n"
                f"💡 **Aplicación práctica:** Los profesionales aplican este principio para salvaguardar la infraestructura, "
                f"garantizar cumplimiento normativo y responder efectivamente ante incidentes en entornos reales de producción."
            )
            question_data = {
                "scenario": f"Durante la evaluación de seguridad en '{self.title}', el equipo analiza los requerimientos de '{c_title}'.",
                "question": f"¿Cuál de las siguientes opciones describe de manera precisa y oficial el principio de '{c_title}'?",
                "options": [
                    f"A) {c_detail}",
                    "B) Es un procedimiento puramente administrativo sin impacto en la postura de seguridad operativa.",
                    "C) Representa una directriz obsoleta que fue descontinuada en los estándares modernos de la industria.",
                    "D) Se aplica exclusivamente a estaciones de trabajo cliente, quedando exentos los servidores y la nube.",
                ],
                "answer": "A",
                "explanation": f"¡Correcto! En {self.domain}, {c_title} se define fundamentalmente como: {c_detail}.",
            }
            steps.append(ModuleConceptStep(
                step_id=f"step_{i}",
                concept_title=c_title,
                explanation=explanation,
                check_question=question_data,
            ))
        return steps

    def get_difficult_exam_questions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Obtiene el banco de preguntas desafiantes de escenario para el examen del módulo."""
        if self.difficult_exam:
            return self.difficult_exam[:count]
        diff_questions = []
        for i, c in enumerate(self.concepts[:count], 1):
            parts = c.split(":", 1)
            c_title = parts[0].strip() if len(parts) > 1 else f"Tema {i}"
            c_detail = parts[1].strip() if len(parts) > 1 else c.strip()
            diff_questions.append({
                "cert_id": "",
                "domain": self.domain,
                "scenario": f"ESCENARIO DESAFIANTE: Un incidente de alta severidad ocurre en la infraestructura corporativa afectando directamente '{c_title}'. La gerencia de operaciones exige una respuesta inmediata alineada con las mejores prácticas oficiales de la certificación.",
                "question": f"Ante esta situación crítica, ¿cuál es la decisión prioritaria que un profesional certificado debe tomar con respecto a '{c_title}'?",
                "options": [
                    f"A) Aplicar los controles oficiales de mitigación: {c_detail}",
                    "B) Desactivar temporalmente los registros de auditoría y firewalls para reducir latencia.",
                    "C) Declarar de inmediato el fin del incidente sin realizar análisis forense ni lecciones aprendidas.",
                    "D) Asumir el riesgo de manera informal sin documentarlo ni notificar a los custodios de datos.",
                ],
                "answer": "A",
                "explanation": f"En situaciones críticas de examen oficial, la respuesta correcta debe apegarse estrictamente a las directrices oficiales: {c_detail}.",
            })
        return diff_questions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "title": self.title,
            "concepts": self.concepts,
            "exam_tips": self.exam_tips,
            "recommended_labs": self.recommended_labs,
            "free_resources": self.free_resources,
            "concept_steps": [s.to_dict() for s in self.get_concept_steps()],
            "difficult_exam": self.difficult_exam,
        }


@dataclass
class CertificationInfo:
    """Ficha curricular completa de una certificación de ciberseguridad."""
    cert_id: str
    name: str
    vendor: str
    level: str
    exam_format: str
    passing_score: str
    passing_percentage: float
    description: str
    official_url: str
    domains: List[Dict[str, Any]]
    study_topics: List[StudyTopic]
    aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cert_id": self.cert_id,
            "name": self.name,
            "vendor": self.vendor,
            "level": self.level,
            "exam_format": self.exam_format,
            "passing_score": self.passing_score,
            "passing_percentage": self.passing_percentage,
            "description": self.description,
            "official_url": self.official_url,
            "domains": self.domains,
            "study_topics": [t.to_dict() for t in self.study_topics],
            "aliases": self.aliases,
        }


CERTIFICATION_CATALOG: Dict[str, CertificationInfo] = {
    "isc2_cc": CertificationInfo(
        cert_id="isc2_cc",
        name="Certified in Cybersecurity (CC)",
        vendor="ISC2",
        level="Entry Level (Principiante)",
        exam_format="100 preguntas de opción múltiple (120 minutos)",
        passing_score="700 / 1000 puntos escalados",
        passing_percentage=70.0,
        description="Certificación fundacional de ISC2 ideal para iniciar carrera en ciberseguridad sin experiencia técnica previa requerida.",
        official_url="https://www.isc2.org/certifications/cc",
        aliases=["isc2", "cc", "isc2_cc", "isc2 cc", "certified in cybersecurity", "isc"],
        domains=[
            {"name": "Domain 1: Security Principles", "weight": "26%"},
            {"name": "Domain 2: Incident Response, BC & DR", "weight": "10%"},
            {"name": "Domain 3: Access Controls Concepts", "weight": "22%"},
            {"name": "Domain 4: Network Security", "weight": "24%"},
            {"name": "Domain 5: Security Operations", "weight": "18%"},
        ],
        study_topics=[
            StudyTopic(
                domain="Domain 1: Security Principles",
                title="Fundamentos de Seguridad de la Información y Gestión del Riesgo",
                concepts=[
                    "Tríada CIA: Confidencialidad (cifrado, permisos), Integridad (hashes, firmas digitales), Disponibilidad (redundancia, backups).",
                    "Autenticación vs Autorización vs Contabilidad (AAA).",
                    "No Repudio: Garantía matemática de que el emisor no puede negar el envío de un mensaje.",
                    "Gestión del Riesgo: Amenaza (Threat) x Vulnerabilidad (Vulnerability) x Impacto (Impact).",
                    "Tratamiento del riesgo: Mitigar, Aceptar, Transferir (seguros) y Evitar.",
                    "Políticas, Estándares, Procedimientos y Guías organizacionales.",
                ],
                exam_tips=[
                    "ISC2 prioriza el pensamiento de liderazgo/gestión: la seguridad de la vida humana (Life Safety) siempre es la máxima prioridad indiscutible.",
                    "Diferencia claramente entre 'Aceptar un riesgo' (decisión formal documentada) e 'Ignorar un riesgo' (negligencia inaceptable).",
                ],
                recommended_labs=[
                    "TryHackMe: Principles of Security Room (Free)",
                    "Cisco Skills for All: Introduction to Cybersecurity",
                ],
                free_resources=[
                    {"name": "ISC2 Free One Million CC Training", "url": "https://www.isc2.org/landing/1mcc"},
                    {"name": "NIST SP 800-30: Risk Assessment Guide", "url": "https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final"},
                ],
                concept_steps=[
                    ModuleConceptStep(
                        step_id="step_1",
                        concept_title="Tríada CIA (Confidencialidad, Integridad y Disponibilidad)",
                        explanation=(
                            "La Tríada CIA es la piedra angular de toda la seguridad de la información:\n\n"
                            "1. **Confidencialidad (Confidentiality)**: Asegura que la información solo sea vista por personas autorizadas. Se protege con cifrado (ej. AES-256), controles de acceso y clasificación de datos.\n"
                            "2. **Integridad (Integrity)**: Garantiza que los datos no hayan sido alterados o corrompidos de forma no autorizada. Se verifica mediante funciones hash (ej. SHA-256) y firmas digitales.\n"
                            "3. **Disponibilidad (Availability)**: Garantiza que los sistemas y servicios estén operativos cuando los usuarios legítimos los necesiten. Se asegura con redundancia (RAID, balanceadores de carga) y backups."
                        ),
                        check_question={
                            "scenario": "Un empleado descontento modifica sigilosamente las cifras contables en la base de datos de nóminas para asignarse una bonificación indebida.",
                            "question": "¿Qué pilar fundamental de la Tríada CIA ha sido directamente vulnerado en este incidente?",
                            "options": [
                                "A) Confidencialidad",
                                "B) Integridad",
                                "C) Disponibilidad",
                                "D) No Repudio",
                            ],
                            "answer": "B",
                            "explanation": "La modificación no autorizada de datos rompe directamente la Integridad, ya que la información contable ha dejado de ser exacta y confiable.",
                        },
                    ),
                    ModuleConceptStep(
                        step_id="step_2",
                        concept_title="Modelo AAA (Autenticación, Autorización y Contabilidad) y No Repudio",
                        explanation=(
                            "El modelo AAA gobierna el control de acceso:\n\n"
                            "1. **Identificación**: Afirmar quién eres (ej. ingresar tu nombre de usuario).\n"
                            "2. **Autenticación (Authentication)**: Demostrar fehacientemente que eres quien dices ser (contraseña, token OTP o huella dactilar).\n"
                            "3. **Autorización (Authorization)**: Definir a qué recursos tienes permiso de acceder una vez autenticado.\n"
                            "4. **Contabilidad / Auditoría (Accounting)**: Registrar en logs qué acciones hiciste, a qué hora y desde dónde.\n"
                            "5. **No Repudio (Non-Repudiation)**: Garantía criptográfica (firmas digitales) que impide que el emisor niegue haber enviado un mensaje o ejecutado una acción."
                        ),
                        check_question={
                            "scenario": "Un usuario ingresa su contraseña correctamente, pero al intentar borrar un archivo en un recurso compartido recibe el mensaje 'Acceso Denegado: Permisos insuficientes'.",
                            "question": "¿Qué función del modelo AAA está bloqueando la solicitud del usuario?",
                            "options": [
                                "A) Identificación",
                                "B) Autenticación",
                                "C) Autorización",
                                "D) Contabilidad",
                            ],
                            "answer": "C",
                            "explanation": "El usuario ya fue autenticado (se demostró su identidad), pero la Autorización determinó que su rol carece de permisos de escritura o eliminación.",
                        },
                    ),
                    ModuleConceptStep(
                        step_id="step_3",
                        concept_title="Ecuación y Gestión del Riesgo (Amenaza, Vulnerabilidad e Impacto)",
                        explanation=(
                            "El riesgo en ciberseguridad se calcula mediante la relación:\n\n"
                            "$$\\text{Riesgo} = \\text{Amenaza} \\times \\text{Vulnerabilidad} \\times \\text{Impacto}$$\n\n"
                            "- **Amenaza (Threat)**: Agente o evento externo potencial de causar daño (ej. ransomware, atacante, desastre natural).\n"
                            "- **Vulnerabilidad (Vulnerability)**: Debilidad o fallo interno en el sistema que puede ser explotado (ej. puerto abierto, software sin parchar).\n"
                            "- **Impacto (Impact)**: Costo o magnitud del daño ocasionado si la vulnerabilidad es explotada."
                        ),
                        check_question={
                            "scenario": "Un servidor web tiene una vulnerabilidad crítica RCE (Ejecución Remota de Código), pero se encuentra completamente aislado en una red privada sin salida a Internet ni comunicación con otros hosts.",
                            "question": "Al no existir un vector de amenaza externa con acceso al servidor, ¿qué ocurre con el riesgo operativo?",
                            "options": [
                                "A) Se reduce drásticamente porque la probabilidad de que una amenaza externa alcance la vulnerabilidad es mínima.",
                                "B) Se transforma automáticamente en un riesgo reputacional incontrolable.",
                                "C) Se multiplica exponencialmente por el tipo de sistema operativo base.",
                                "D) Elimina la necesidad de aplicar actualizaciones de seguridad de por vida.",
                            ],
                            "answer": "A",
                            "explanation": "Para que exista un riesgo materializable, una amenaza debe poder interactuar con la vulnerabilidad. Sin un vector de ataque viable, el riesgo global es significativamente menor.",
                        },
                    ),
                    ModuleConceptStep(
                        step_id="step_4",
                        concept_title="Estrategias de Tratamiento del Riesgo (Mitigar, Aceptar, Transferir, Evitar)",
                        explanation=(
                            "Una vez evaluado el riesgo, la gerencia formaliza su tratamiento mediante 4 estrategias oficiales:\n\n"
                            "1. **Mitigar (Mitigate)**: Implementar controles para reducir la probabilidad o el impacto (ej. instalar un firewall, parchar o capacitar).\n"
                            "2. **Transferir (Transfer)**: Trasladar el impacto financiero a un tercero (ej. contratar un seguro de ciberseguridad o subcontratar con SLA).\n"
                            "3. **Aceptar (Accept)**: Asumir formalmente el riesgo residual cuando el costo de mitigarlo supera el valor del activo. Debe ser una decisión documentada.\n"
                            "4. **Evitar (Avoid)**: Detener la actividad o desconectar el servicio inseguro para eliminar el riesgo por completo.\n\n"
                            "⚠️ *Trampa de Examen:* Ignorar un riesgo NO es una estrategia válida, es negligencia administrativa inaceptable."
                        ),
                        check_question={
                            "scenario": "Una compañía contrata una póliza de seguros de ciberriesgo por $5,000,000 para cubrir posibles rescates y pérdidas operativas de ransomware.",
                            "question": "¿Qué estrategia formal de tratamiento del riesgo se ha implementado en este caso?",
                            "options": [
                                "A) Mitigación técnica del riesgo",
                                "B) Transferencia del riesgo",
                                "C) Evitación del riesgo",
                                "D) Aceptación implícita",
                            ],
                            "answer": "B",
                            "explanation": "Contratar un seguro o trasladar la carga financiera a una entidad aseguradora es el ejemplo canónico de Transferencia del Riesgo.",
                        },
                    ),
                    ModuleConceptStep(
                        step_id="step_5",
                        concept_title="Gobernanza de Seguridad y la Regla de Oro (Life Safety)",
                        explanation=(
                            "La estructura de gobernanza define las reglas organizacionales:\n\n"
                            "1. **Políticas (Policies)**: Obligatorias y de alto nivel dictadas por la dirección ('qué se debe hacer').\n"
                            "2. **Estándares (Standards)**: Especificaciones tecnológicas uniformes obligatorias (ej. 'usar AES-256 en discos duros').\n"
                            "3. **Procedimientos (Procedures)**: Pasos detallados paso a paso ('cómo ejecutar la tarea').\n"
                            "4. **Guías (Guidelines)**: Mejores prácticas recomendadas pero flexibles.\n\n"
                            "🚨 **REGLA DE ORO DE ISC2:** En cualquier situación de emergencia o desastre, la **Seguridad de la Vida Humana (Life Safety)** es siempre la prioridad máxima indiscutible por encima de cualquier activo o dato."
                        ),
                        check_question={
                            "scenario": "Durante una alarma de incendio en el centro de datos, las puertas automáticas de evacuación se bloquean con cerraduras electrónicas para impedir que alguien robe un servidor con secretos comerciales, atrapando a los operadores.",
                            "question": "¿Qué principio supremo de seguridad física y de ISC2 se está violando de forma inaceptable?",
                            "options": [
                                "A) Mínimo Privilegio",
                                "B) Prioridad Suprema de la Vida Humana (Life Safety)",
                                "C) Separación de Funciones",
                                "D) Defensa en Profundidad",
                            ],
                            "answer": "B",
                            "explanation": "La protección de la vida humana (Life Safety) es siempre la prioridad número uno por encima de cualquier información clasificada o activo de hardware.",
                        },
                    ),
                ],
                difficult_exam=[
                    {
                        "cert_id": "isc2_cc",
                        "domain": "Domain 1: Security Principles",
                        "scenario": "Un banco internacional diseña una nueva arquitectura de pagos en la nube. Durante la revisión del CISO, se identifica que un fallo en la API podría exponer números de tarjetas o paralizar el servicio de cobros a nivel global, pero contratar una póliza de seguro y redundancia activa costaría el 30% del presupuesto anual.",
                        "question": "¿Cuál es la primera acción que el equipo de gobernanza debe ejecutar antes de decidir si mitigar, transferir o aceptar el riesgo?",
                        "options": [
                            "A) Realizar una evaluación formal de riesgos (Risk Assessment) calculando el ALE (Annualized Loss Expectancy) y el impacto en los activos.",
                            "B) Desactivar inmediatamente la API y cancelar el lanzamiento del producto sin consultar a la directiva.",
                            "C) Firmar una aceptación informal del riesgo en un correo electrónico interno.",
                            "D) Contratar de inmediato al proveedor de seguros más económico sin evaluar el SLA.",
                        ],
                        "answer": "A",
                        "explanation": "Antes de tomar cualquier decisión de tratamiento del riesgo, la gobernanza exige una evaluación formal de riesgos (Risk Assessment) cuantitativa o cualitativa para conocer el impacto real y el valor de los activos en riesgo.",
                    },
                    {
                        "cert_id": "isc2_cc",
                        "domain": "Domain 1: Security Principles",
                        "scenario": "Una empresa de telecomunicaciones sufre un incidente donde un operador no autorizado utilizó las credenciales del Administrador para apagar tres enrutadores de red troncal. El administrador original jura que él estaba de vacaciones en otro país en ese momento.",
                        "question": "¿Qué control técnico y conceptual faltó implementar para garantizar el principio de No Repudio y evitar el uso compartido de identidades?",
                        "options": [
                            "A) Autenticación multifactor individual vinculada a cuentas nominativas intransferibles con registro criptográfico de sesiones.",
                            "B) Aumentar la longitud de la contraseña compartida del administrador a 64 caracteres.",
                            "C) Desconectar los enrutadores de la red troncal durante las vacaciones del personal.",
                            "D) Desactivar los registros de auditoría Syslog para evitar que se saturen de eventos.",
                        ],
                        "answer": "A",
                        "explanation": "El no repudio y la contabilidad efectiva requieren cuentas individuales (no compartidas) y autenticación robusta como MFA para vincular indiscutiblemente las acciones a una persona específica.",
                    },
                    {
                        "cert_id": "isc2_cc",
                        "domain": "Domain 1: Security Principles",
                        "scenario": "En una planta nuclear, un ataque cibernético desactiva el sistema de enfriamiento primario y simultáneamente activa las alarmas de incendio en la sala de control.",
                        "question": "De acuerdo con el Código de Ética y los principios de ISC2, ¿cuál debe ser la primera prioridad absoluta de los procedimientos de respuesta?",
                        "options": [
                            "A) Garantizar la seguridad física y evacuación inmediata del personal humano (Life Safety).",
                            "B) Recuperar las copias de seguridad de los controladores lógicos programables (PLC).",
                            "C) Preservar la evidencia digital en la memoria volátil de los servidores SCADA para el análisis forense.",
                            "D) Emitir un comunicado de prensa para proteger la reputación corporativa.",
                        ],
                        "answer": "A",
                        "explanation": "En las certificaciones ISC2, la preservación de la vida humana (Life Safety) es la prioridad número 1 indiscutible en cualquier escenario de catástrofe o ciberataque.",
                    },
                    {
                        "cert_id": "isc2_cc",
                        "domain": "Domain 1: Security Principles",
                        "scenario": "La gerencia de TI decide sustituir la política de contraseñas complejas por un sistema de Single Sign-On (SSO) con claves de paso FIDO2 y autenticación biométrica en todos los dispositivos corporativos.",
                        "question": "¿Cómo debe formalizarse este cambio dentro de la estructura jerárquica de gobernanza de seguridad?",
                        "options": [
                            "A) Actualizar la Política de Seguridad de la Información aprobada por la dirección y definir los nuevos Estándares y Procedimientos de autenticación.",
                            "B) Publicar únicamente una Guía opcional en la intranet sin modificar estándares técnicos.",
                            "C) Implementar el cambio directamente en producción sin documentar políticas ni capacitar a usuarios.",
                            "D) Mantener la política antigua en secreto para no confundir a los auditores externos.",
                        ],
                        "answer": "A",
                        "explanation": "Los cambios arquitectónicos deben respaldarse en la jerarquía documental: actualizar la Política aprobada por la gerencia y plasmar las especificaciones técnicas obligatorias en los Estándares correspondientes.",
                    },
                    {
                        "cert_id": "isc2_cc",
                        "domain": "Domain 1: Security Principles",
                        "scenario": "Un auditor descubre que una aplicación procesa datos financieros sensibles en texto claro dentro de la memoria compartida entre dos microservicios en el mismo host.",
                        "question": "¿Qué par de pilares de la seguridad de la información se encuentran en riesgo directo si un atacante obtiene acceso de lectura y escritura en la memoria del host?",
                        "options": [
                            "A) Confidencialidad e Integridad de los datos financieros.",
                            "B) Disponibilidad y Recuperación ante Desastres únicamente.",
                            "C) Principio de No Repudio legal exclusivamente.",
                            "D) Continuidad de negocio sin impacto en la información.",
                        ],
                        "answer": "A",
                        "explanation": "El acceso de lectura no autorizado compromete la Confidencialidad, mientras que la capacidad de alterar o manipular la memoria compromete la Integridad de los registros financieros.",
                    },
                ],
            ),
            StudyTopic(
                domain="Domain 2: Incident Response, BC & DR",
                title="Respuesta a Incidentes, Continuidad de Negocio y Recuperación ante Desastres",
                concepts=[
                    "Ciclo de Respuesta a Incidentes (NIST): Preparación, Detección y Análisis, Contención/Erradicación/Recuperación, Actividad Post-Incidente (Lecciones Aprendidas).",
                    "Continuidad del Negocio (BCP) vs Recuperación ante Desastres (DRP): BCP mantiene operaciones críticas; DRP restaura sistemas TI tras la catástrofe.",
                    "Métricas RTO (Recovery Time Objective) y RPO (Recovery Point Objective): RTO es tiempo máximo admisible de parada; RPO es pérdida máxima admisible de datos.",
                    "Sitios de recuperación: Hot Site (listo en minutos, más caro), Warm Site (horas/días, hardware sin datos actuales), Cold Site (espacio físico vacío).",
                ],
                exam_tips=[
                    "Si una pregunta menciona 'pérdida de datos en horas o transacciones', la respuesta suele ser RPO; si menciona 'tiempo que la empresa puede esperar a que el servidor vuelva a encender', es RTO.",
                ],
                recommended_labs=[
                    "TryHackMe: Incident Handling Fundamentals (Free)",
                ],
                free_resources=[
                    {"name": "NIST SP 800-61 Rev 2: Computer Security Incident Handling", "url": "https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final"},
                ],
            ),
            StudyTopic(
                domain="Domain 3: Access Controls Concepts",
                title="Modelos de Control de Acceso Físico y Lógico",
                concepts=[
                    "Controles de Acceso Físicos (torniquetes, guardias, cámaras CCTV, mantrap) vs Lógicos/Técnicos (ACLs, firewalls, cifrado).",
                    "Modelos de Control: DAC (Discretionary, el dueño decide), MAC (Mandatory, etiquetas de seguridad y clasificaciones como Secreto/Top Secret), RBAC (Role-Based, según el rol laboral).",
                    "Principio de Menor Privilegio (Least Privilege) y Separación de Funciones (Separation of Duties).",
                    "Autenticación Multifactor (MFA): Debe combinar factores de categorías distintas: Algo que sabes (contraseña), Algo que tienes (token/llave FIDO2) y Algo que eres (biometría). Dos contraseñas NO es MFA.",
                ],
                exam_tips=[
                    "Típica trampa de examen: ingresar una contraseña y un PIN es autenticación de factor único repetido (ambos son 'algo que sabes').",
                ],
                recommended_labs=[
                    "TryHackMe: Authentication Bypass (Free)",
                ],
                free_resources=[
                    {"name": "OWASP Authentication Cheat Sheet", "url": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"},
                ],
            ),
            StudyTopic(
                domain="Domain 4: Network Security",
                title="Arquitectura de Red, Protocolos Seguros y Amenazas",
                concepts=[
                    "Modelo OSI vs TCP/IP y puertos esenciales: DNS (53), HTTP (80), HTTPS (443), SSH (22), RDP (3389).",
                    "Protocolos inseguros vs sus contrapartes seguras: Telnet -> SSH, HTTP -> HTTPS, FTP -> SFTP, SNMPv1/v2 -> SNMPv3.",
                    "Dispositivos de red: Firewalls (filtrado de paquetes e inspección de estado), IDS (detección pasiva) e IPS (prevención y bloqueo activo en línea).",
                    "VLANs, DMZ (Zona Desmilitarizada) para servidores públicos y Segmentación de Red.",
                    "Ataques de red: Man-in-the-Middle (MitM), Spoofing de ARP/DNS, Denegación de Servicio (DoS/DDoS).",
                ],
                exam_tips=[
                    "En ISC2 CC, siempre recuerda que un IDS solo genera alertas (pasivo), mientras que un IPS se coloca 'in-line' para bloquear tráfico en tiempo real.",
                ],
                recommended_labs=[
                    "Cisco Skills for All: Networking Basics (Free)",
                    "OverTheWire: Bandit (Comandos y redes)",
                ],
                free_resources=[
                    {"name": "Professor Messer Network Security Notes", "url": "https://www.professormesser.com/"},
                ],
            ),
            StudyTopic(
                domain="Domain 5: Security Operations",
                title="Operaciones de Seguridad, Hardening y Protección de Datos",
                concepts=[
                    "Ciclo de vida del dato: Creación, Almacenamiento, Uso, Compartición, Archivo y Destrucción.",
                    "Destrucción segura de datos: Sobrescritura (Wiping), Desmagnetización (Degaussing) y Destrucción Física (Shredding/Incineración).",
                    "Hardening de sistemas: Deshabilitar servicios y puertos innecesarios, cambio de contraseñas por defecto, gestión de parches.",
                    "Cifrado en reposo (At Rest), en tránsito (In Transit) y en uso (In Use).",
                    "Concienciación y entrenamiento del personal contra Ingeniería Social (Phishing, Vishing, Smishing).",
                ],
                exam_tips=[
                    "Formatear un disco duro convencional NO destruye los datos de forma segura para los estándares forenses; se requiere wiping criptográfico o destrucción física.",
                ],
                recommended_labs=[
                    "TryHackMe: Security Operations Room (Free)",
                ],
                free_resources=[
                    {"name": "CIS Benchmarks (Center for Internet Security)", "url": "https://www.cisecurity.org/cis-benchmarks"},
                ],
            ),
        ],
    ),

    "comptia_secplus": CertificationInfo(
        cert_id="comptia_secplus",
        name="CompTIA Security+ (SY0-701)",
        vendor="CompTIA",
        level="Entry/Intermediate (Estándar Global)",
        exam_format="Hasta 90 preguntas (Opción múltiple + PBQs prácticas) (90 minutos)",
        passing_score="750 / 900 puntos escalados (~83%)",
        passing_percentage=83.3,
        description="La certificación de ciberseguridad más reconocida en la industria global. Cumple con la directiva DoD 8570/8140.",
        official_url="https://www.comptia.org/certifications/security",
        aliases=["sec+", "secplus", "security+", "securityplus", "sy0-701", "sy0701", "comptia sec+"],
        domains=[
            {"name": "1.0 General Security Concepts", "weight": "12%"},
            {"name": "2.0 Threats, Vulnerabilities & Mitigations", "weight": "22%"},
            {"name": "3.0 Security Architecture", "weight": "18%"},
            {"name": "4.0 Security Operations", "weight": "28%"},
            {"name": "5.0 Security Program Management & Oversight", "weight": "20%"},
        ],
        study_topics=[
            StudyTopic(
                domain="1.0 General Security Concepts",
                title="Conceptos Fundamentales de Seguridad y Criptografía",
                concepts=[
                    "Arquitectura Zero Trust (ZTA): 'Nunca confíes, siempre verifica'. Inspección continua y micro-segmentación.",
                    "Criptografía Simétrica (AES, ChaCha20 - rápida, misma clave) vs Asimétrica (RSA, ECC - clave pública/privada).",
                    "Funciones Hash criptográficas (SHA-256, SHA-3) para integridad.",
                    "Infraestructura de Clave Pública (PKI): Certificados X.509, Autoridades de Certificación (CA), CRL y OCSP.",
                ],
                exam_tips=[
                    "En SY0-701, Zero Trust es el paradigma rector. Si preguntan por asegurar accesos entre servicios internos, busca Zero Trust o microsegmentación.",
                ],
                recommended_labs=[
                    "TryHackMe: Cryptography Room (Free)",
                ],
                free_resources=[
                    {"name": "Professor Messer SY0-701 Free Video Course", "url": "https://www.professormesser.com/security-plus/sy0-701/sy0-701-video/sy0-701-training-course/"},
                ],
            ),
            StudyTopic(
                domain="2.0 Threats, Vulnerabilities & Mitigations",
                title="Vectores de Ataque, Malware y Mitigaciones Técnicas",
                concepts=[
                    "Tipos de malware: Ransomware, Rootkits (a nivel de kernel), Keyloggers, Spyware, Caballos de Troya.",
                    "Ataques a aplicaciones: SQLi, Cross-Site Scripting (XSS reflejado, almacenado y DOM), SSRF, CSRF.",
                    "Vulnerabilidades de red: ARP Poisoning, DNS Sinkholing, Rogue DHCP, Ataques de Deautenticación Wi-Fi.",
                    "Ingeniería Social: Phishing masivo, Spear Phishing (objetivo específico), Whaling (directivos ejecutivos).",
                ],
                exam_tips=[
                    "Para PBQs de Security+: Memoriza los indicadores de ataque en logs de firewall y Apache/Nginx para identificar SQLi (`' OR '1'='1`) o XSS (`<script>`).",
                ],
                recommended_labs=[
                    "PortSwigger Web Security Academy (Free)",
                    "TryHackMe: OWASP Top 10 (Free)",
                ],
                free_resources=[
                    {"name": "MITRE ATT&CK Matrix", "url": "https://attack.mitre.org/"},
                ],
            ),
            StudyTopic(
                domain="3.0 Security Architecture",
                title="Arquitectura de Seguridad, Nube e Infraestructura",
                concepts=[
                    "Modelos de Nube: IaaS, PaaS, SaaS y Responsabilidad Compartida (Shared Responsibility Model).",
                    "Contenedores y Virtualización: Seguridad en Docker, Kubernetes y aislamiento de namespaces/cgroups.",
                    "Resiliencia y Alta Disponibilidad: Balanceadores de carga, clústeres redundantes, RAID y arquitecturas multisitio.",
                ],
                exam_tips=[
                    "En SaaS el proveedor gestiona casi todo; en IaaS tú como cliente eres responsable del SO, parches y aplicaciones.",
                ],
                recommended_labs=[
                    "Cisco Skills for All: Cloud Security Basics (Free)",
                ],
                free_resources=[
                    {"name": "Cloud Security Alliance (CSA) Guidance", "url": "https://cloudsecurityalliance.org/"},
                ],
            ),
            StudyTopic(
                domain="4.0 Security Operations",
                title="Operaciones de Seguridad, SIEM, SOAR y Gestión de Logs",
                concepts=[
                    "Monitorización: SIEM (centralización y correlación de eventos) y SOAR (orquestación y respuesta automatizada con playbooks).",
                    "Herramientas de diagnóstico: Nmap (escaneo), Wireshark (captura), tcpdump, netstat, curl.",
                    "Forense Digital: Cadena de custodia, orden de volatilidad (Registros/Caché -> RAM -> Estado de red -> Disco duro -> Medios de backup).",
                ],
                exam_tips=[
                    "La volatilidad SIEMPRE cae en examen: La memoria RAM es más volátil que el disco duro; nunca apagues la máquina si necesitas capturar evidencia volátil.",
                ],
                recommended_labs=[
                    "TryHackMe: Splunk Basics (Free)",
                    "TryHackMe: Wireshark 101 (Free)",
                ],
                free_resources=[
                    {"name": "Security+ SY0-701 Exam Objectives PDF", "url": "https://www.comptia.jp/pdf/CompTIA%20Security+%20SY0-701%20Exam%20Objectives.pdf"},
                ],
            ),
            StudyTopic(
                domain="5.0 Security Program Management & Oversight",
                title="Gobernanza, Gestión de Riesgos y Cumplimiento Normativo",
                concepts=[
                    "Marcos de Control: NIST CSF 2.0 (Govern, Identify, Protect, Detect, Respond, Recover), ISO/IEC 27001.",
                    "Leyes y Regulaciones: GDPR, HIPAA, PCI DSS y soberanía de datos.",
                    "Evaluación Cuantitativa de Riesgos: SLE (Single Loss Expectancy) x ARO (Annualized Rate of Occurrence) = ALE (Annualized Loss Expectancy).",
                    "Gestión de Riesgos de Terceros (Supply Chain): SLA, MOU, BPA, auditorías SOC 2 Tipo II.",
                ],
                exam_tips=[
                    "Fórmula clásica en Security+: ALE = SLE x ARO. Además, recuerda que SOC 2 Tipo II evalúa la efectividad operativa de los controles a lo largo del tiempo, no solo en un punto fijo.",
                ],
                recommended_labs=[
                    "TryHackMe: Governance & Regulation (Free)",
                ],
                free_resources=[
                    {"name": "NIST Cybersecurity Framework", "url": "https://www.nist.gov/cyberframework"},
                ],
            ),
        ],
    ),

    "comptia_netplus": CertificationInfo(
        cert_id="comptia_netplus",
        name="CompTIA Network+ (N10-008)",
        vendor="CompTIA",
        level="Entry Level (Infraestructura)",
        exam_format="Hasta 90 preguntas (Test + PBQs) (90 minutos)",
        passing_score="720 / 900 puntos escalados (~80%)",
        passing_percentage=80.0,
        description="Establece los cimientos indispensables de redes, protocolos TCP/IP, subredes, switches y routing para cualquier analista de ciberseguridad.",
        official_url="https://www.comptia.org/certifications/network",
        aliases=["net+", "netplus", "network+", "n10-008", "n10008", "comptia net+"],
        domains=[
            {"name": "1.0 Networking Fundamentals", "weight": "24%"},
            {"name": "2.0 Network Implementations", "weight": "19%"},
            {"name": "3.0 Network Operations", "weight": "16%"},
            {"name": "4.0 Network Security", "weight": "19%"},
            {"name": "5.0 Network Troubleshooting", "weight": "22%"},
        ],
        study_topics=[
            StudyTopic(
                domain="1.0 Networking Fundamentals",
                title="Modelo OSI, Subnetting y Protocolos de Enrutamiento",
                concepts=[
                    "Capas OSI: Física, Enlace, Red, Transporte, Sesión, Presentación, Aplicación.",
                    "Subnetting IPv4 y VLSM: Cálculo rápido de máscaras (/24 = 254 hosts, /28 = 14 hosts).",
                    "Protocolos de enrutamiento: OSPF (estado de enlace), BGP (vector de rutas de Internet).",
                    "Direcciones privadas RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 y APIPA (169.254.x.x).",
                ],
                exam_tips=[
                    "Si una interfaz obtiene una dirección 169.254.x.x significa que no pudo comunicarse con el servidor DHCP (APIPA).",
                ],
                recommended_labs=[
                    "Cisco Skills for All: Networking Basics",
                ],
                free_resources=[
                    {"name": "Professor Messer Network+ Course", "url": "https://www.professormesser.com/network-plus/n10-008/n10-008-training-course/"},
                ],
            ),
            StudyTopic(
                domain="2.0 Network Implementations",
                title="Routing, Switching, VLANs y Redes Inalámbricas",
                concepts=[
                    "VLANs (802.1Q) y Enlaces Troncales (Trunking).",
                    "Spanning Tree Protocol (STP / 802.1D): Prevención de bucles de capa 2 en switches.",
                    "Estándares Wi-Fi: 802.11ac (Wi-Fi 5) y 802.11ax (Wi-Fi 6), frecuencias 2.4 GHz vs 5 GHz vs 6 GHz.",
                ],
                exam_tips=[
                    "STP bloquea puertos redundantes para evitar tormentas de difusión (broadcast storms).",
                ],
                recommended_labs=[
                    "TryHackMe: Intro to LAN (Free)",
                ],
                free_resources=[
                    {"name": "Cisco Packet Tracer Tutorials", "url": "https://skillsforall.com/"},
                ],
            ),
            StudyTopic(
                domain="3.0 Network Operations",
                title="Monitorización, Gestión de Configuración y Alta Disponibilidad",
                concepts=[
                    "Monitorización: SNMPv3 (con autenticación y cifrado SHA/AES), Syslog (puerto UDP 514).",
                    "Alta disponibilidad: FHRP (First Hop Redundancy Protocol como VRRP y HSRP).",
                    "Documentación de red: Diagramas físicos vs lógicos, líneas base de rendimiento (baselines).",
                ],
                exam_tips=[
                    "SNMPv1 y v2c transmiten 'community strings' en texto plano; en entornos seguros siempre debe usarse SNMPv3.",
                ],
                recommended_labs=[
                    "TryHackMe: Network Services (Free)",
                ],
                free_resources=[
                    {"name": "Wireshark Network Analysis Guide", "url": "https://www.wireshark.org/"},
                ],
            ),
            StudyTopic(
                domain="4.0 Network Security",
                title="Ataques a Redes, Defensas Perimetrales y Autenticación",
                concepts=[
                    "Defensas: Listas de Control de Acceso (ACLs estándar y extendidas), DMZ, Firewalls con inspección de estado.",
                    "Ataques: Spoofing de ARP, DNS Poisoning, VLAN Hopping, Rogue Access Points y Evil Twin.",
                    "Autenticación de acceso a red: 802.1X, servidores RADIUS y TACACS+.",
                ],
                exam_tips=[
                    "RADIUS cifra únicamente la contraseña en el paquete; TACACS+ cifra todo el contenido del paquete TCP (puerto 49).",
                ],
                recommended_labs=[
                    "TryHackMe: Network Security Fundamentals (Free)",
                ],
                free_resources=[
                    {"name": "OWASP Network Security Cheat Sheet", "url": "https://cheatsheetseries.owasp.org/"},
                ],
            ),
            StudyTopic(
                domain="5.0 Network Troubleshooting",
                title="Resolución Metódica de Incidencias y Herramientas de Red",
                concepts=[
                    "Metodología de troubleshooting de 7 pasos de CompTIA: Identificar problema, Establecer teoría, Probar teoría, Plan de acción, Verificar funcionalidad completa, Documentar hallazgos.",
                    "Herramientas de software: `ping` (ICMP), `traceroute`/`tracert`, `netstat`/`ss`, `nslookup`/`dig`, `tcpdump`.",
                    "Herramientas de hardware: Comprobadores de cables (cable testers), reflectómetros de dominio de tiempo (TDR), multímetros.",
                ],
                exam_tips=[
                    "Siempre memoriza el paso final de la metodología de troubleshooting: ¡Documentar los hallazgos, acciones y resultados!",
                ],
                recommended_labs=[
                    "OverTheWire: Bandit (Redes y comandos)",
                ],
                free_resources=[
                    {"name": "CompTIA Troubleshooting Framework", "url": "https://www.comptia.org/"},
                ],
            ),
        ],
    ),

    "ejpt": CertificationInfo(
        cert_id="ejpt",
        name="eLearnSecurity Junior Penetration Tester v2 (eJPT)",
        vendor="INE Security",
        level="Práctico Ofensivo Entry-Level",
        exam_format="Examen 100% práctico de 48 horas en laboratorio real con 35 preguntas basadas en objetivos",
        passing_score="70% de preguntas del examen resueltas con éxito",
        passing_percentage=70.0,
        description="Certificación práctica de hacking ético de referencia para principiantes. Evalúa reconocimiento real, escaneo, explotación y pivoteo en red.",
        official_url="https://ine.com/certifications/ejpt-v2",
        aliases=["ejpt", "ejptv2", "ejpt v2", "elearnsecurity", "ine ejpt"],
        domains=[
            {"name": "Assessment Methodologies", "weight": "25%"},
            {"name": "Host & Networking Auditing", "weight": "25%"},
            {"name": "Host & Networking Penetration Testing", "weight": "35%"},
            {"name": "Web Application Penetration Testing", "weight": "15%"},
        ],
        study_topics=[
            StudyTopic(
                domain="Assessment Methodologies",
                title="Metodología de Pentesting y Reconocimiento",
                concepts=[
                    "Fases de un Pentest: Pasos previos, Escaneo/Reconocimiento, Explotación, Post-explotación y Limpieza.",
                    "Reconocimiento pasivo (Whois, Shodan, Google Dorks) vs activo (Nmap, Nikto).",
                    "Reglas de compromiso (Rules of Engagement) y alcance legal (Scope).",
                ],
                exam_tips=[
                    "En el eJPT v2 la enumeración es el 80% del éxito: nunca saltes directo a Metasploit sin haber anotado todas las versiones de servicios y credenciales por defecto.",
                ],
                recommended_labs=[
                    "TryHackMe: Jr Penetration Tester Pathway (Free Rooms)",
                ],
                free_resources=[
                    {"name": "INE eJPT v2 Exam Guide", "url": "https://help.ine.com/hc/en-us/articles/4412574044179-eJPTv2-Certification-Process"},
                ],
            ),
            StudyTopic(
                domain="Host & Networking Auditing",
                title="Escaneo Avanzado de Redes y Enumeración de Servicios",
                concepts=[
                    "Nmap: Banderas críticas `-sC -sV` (scripts por defecto y versiones), `-p-` (todos los puertos), `-T4` y `--min-rate`.",
                    "Enumeración de SMB: `smbclient -L`, `enum4linux-ng`, `crackmapexec / netexec smb`.",
                    "Enumeración de SSH, FTP (acceso anónimo `anonymous:anonymous`), bases de datos (MySQL 3306, PostgreSQL 5432).",
                ],
                exam_tips=[
                    "Comprueba siempre si el FTP permite login anónimo; suele contener notas, llaves SSH o respaldos con contraseñas.",
                ],
                recommended_labs=[
                    "OverTheWire: Bandit Wargame",
                    "TryHackMe: Nmap in depth",
                ],
                free_resources=[
                    {"name": "Pay-Loads All The Things: Network Services", "url": "https://github.com/swisskyrepo/PayloadsAllTheThings"},
                ],
            ),
            StudyTopic(
                domain="Host & Networking Penetration Testing",
                title="Explotación, Pivoting en Red y Escalada de Privilegios",
                concepts=[
                    "Explotación con Metasploit y búsqueda manual con `searchsploit`.",
                    "Banderas SUID en Linux (`find / -perm -u=s -type f 2>/dev/null`) y abusos en GTFOBins.",
                    "Pivoting: Enrutamiento mediante Meterpreter (`autoroute`), proxychains y túneles SSH (`ssh -D 1080` / `chisel`).",
                    "Escalada de privilegios en Windows: Permisos de servicios no entrecomillados (Unquoted Service Paths), Token impersonation.",
                ],
                exam_tips=[
                    "El eJPT v2 incluye máquinas en subredes internas; si comprometes una máquina con dos interfaces de red (ej. 10.x.x.x y 192.168.x.x), debes pivotar para alcanzar la red interna.",
                ],
                recommended_labs=[
                    "TryHackMe: Wreath Network (Pivoting)",
                    "GTFOBins (gtfobins.github.io)",
                ],
                free_resources=[
                    {"name": "GTFOBins Unix SUID Bypass", "url": "https://gtfobins.github.io/"},
                    {"name": "PayloadsAllTheThings Privilege Escalation", "url": "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md"},
                ],
            ),
            StudyTopic(
                domain="Web Application Penetration Testing",
                title="Vulnerabilidades Web en el Pentest",
                concepts=[
                    "Fuzzing de directorios y archivos: `gobuster dir`, `ffuf -u http://... -w wordlist`.",
                    "SQL Injection básica para bypass de login: `' OR 1=1 --` y extracción con SQLMap.",
                    "Fuerza bruta a paneles administrativos: Burp Suite Intruder y Hydra.",
                    "Subida insegura de archivos (Unrestricted File Upload) para obtener Web Shells (`php-reverse-shell.php`).",
                ],
                exam_tips=[
                    "Si descubres un CMS como WordPress o Joomla, ejecuta herramientas especializadas como `wpscan` para enumerar plugins vulnerables.",
                ],
                recommended_labs=[
                    "PortSwigger Web Security Academy: File Upload vulnerabilities",
                    "TryHackMe: Burp Suite Basics",
                ],
                free_resources=[
                    {"name": "OWASP Testing Guide v4", "url": "https://owasp.org/www-project-web-security-testing-guide/"},
                ],
            ),
        ],
    ),

    "cjca": CertificationInfo(
        cert_id="cjca",
        name="Certified Junior Cybersecurity Analyst (CJCA)",
        vendor="TCM Security",
        level="Práctico Defensivo / SOC Entry-Level",
        exam_format="Examen 100% práctico defensivo de 24 horas + 24 horas para entrega de reporte ejecutivo y técnico",
        passing_score="70% en objetivos prácticos y reporte aprobado",
        passing_percentage=70.0,
        description="Certificación práctica de SOC y Blue Team de TCM Security. Evalúa análisis de tráfico PCAP, SIEM/EDR, triage de malware y respuesta a incidentes.",
        official_url="https://certifications.tcm-sec.com/cjca/",
        aliases=["cjca", "tcm cjca", "certified junior cybersecurity analyst", "tcm soc"],
        domains=[
            {"name": "Network Architecture & Traffic Analysis", "weight": "25%"},
            {"name": "Endpoint Security, SIEM & EDR", "weight": "30%"},
            {"name": "Threat Intelligence & MITRE ATT&CK", "weight": "20%"},
            {"name": "Incident Handling & Memory/Disk Triage", "weight": "25%"},
        ],
        study_topics=[
            StudyTopic(
                domain="Network Architecture & Traffic Analysis",
                title="Inspección Forense de Red y Capturas PCAP",
                concepts=[
                    "Filtros de visualización Wireshark: `http.request.method == 'POST'`, `dns.flags.response == 0`, `tcp.flags.reset == 1`.",
                    "Detección de Beaconing C2: Conexiones repetitivas a intervalos constantes hacia IPs externas no categorizadas.",
                    "Extracción de artefactos en Wireshark: File -> Export Objects -> HTTP / SMB.",
                    "Análisis de logs con Zeek/Bro y detección de firmas con Snort/Suricata.",
                ],
                exam_tips=[
                    "En el CJCA, exportar objetos transmitidos por HTTP en capturas de red te permitirá encontrar el payload que el atacante descargó durante el compromiso.",
                ],
                recommended_labs=[
                    "TryHackMe: Wireshark Traffic Analysis (Free)",
                    "Malware-Traffic-Analysis.net (PCAPs de malware real)",
                ],
                free_resources=[
                    {"name": "Wireshark Display Filter Reference", "url": "https://www.wireshark.org/docs/dfref/"},
                ],
            ),
            StudyTopic(
                domain="Endpoint Security, SIEM & EDR",
                title="Análisis de Logs de Windows, Sysmon y Consultas SIEM",
                concepts=[
                    "Event IDs críticos de Windows Security: 4624 (Logon exitoso), 4625 (Logon fallido), 4688 (Creación de nuevo proceso).",
                    "Eventos de Sysmon: Event 1 (Creación de proceso con CommandLine completa y hashes), Event 3 (Conexión de red iniciada), Event 11 (Creación de archivo).",
                    "Búsqueda de amenazas con Splunk (SPL) o Elastic (KQL/Lucene).",
                    "Detección de persistencia: Claves del registro Run/RunOnce, tareas programadas (`schtasks`), servicios nuevos.",
                ],
                exam_tips=[
                    "Sysmon Event 1 con el campo `ParentImage` es la clave para descubrir de dónde vino la infección (ej. `WINWORD.EXE` ejecutando `powershell.exe -enc ...`).",
                ],
                recommended_labs=[
                    "TryHackMe: Windows Event Logs (Free)",
                    "TryHackMe: Sysmon (Free)",
                ],
                free_resources=[
                    {"name": "Ultimate Windows Security Log Encyclopedia", "url": "https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/"},
                ],
            ),
            StudyTopic(
                domain="Threat Intelligence & MITRE ATT&CK",
                title="Mapeo de TTPs, Indicadores de Compromiso (IOCs) y CTI",
                concepts=[
                    "Pirámide del Dolor (Pyramid of Pain de David Bianco): Hash Values (trivial) -> IP Addresses -> Domain Names -> Network/Host Artifacts -> Tools -> TTPs (difícil).",
                    "MITRE ATT&CK Matrix: Tácticas (el 'por qué'), Técnicas (el 'cómo') y Procedimientos (ejecución real).",
                    "Compartición de CTI: Formatos STIX (Structured Threat Information eXpression) y TAXII.",
                ],
                exam_tips=[
                    "Comprender la cúspide de la Pirámide del Dolor: Cambiar los TTPs de un atacante es lo más difícil y doloroso para ellos.",
                ],
                recommended_labs=[
                    "TryHackMe: Threat Intelligence Tools (Free)",
                ],
                free_resources=[
                    {"name": "MITRE ATT&CK Navigator", "url": "https://mitre-attack.github.io/attack-navigator/"},
                ],
            ),
            StudyTopic(
                domain="Incident Handling & Memory/Disk Triage",
                title="Triaje Rápido de Endpoints y Respuesta a Incidentes",
                concepts=[
                    "Herramientas de triaje en vivo: KAPE (Kroll Artifact Parser and Extractor), Velociraptor, CyberChef.",
                    "Artefactos clave de ejecución en Windows: Prefetch (.pf), Amcache.hve, Shimcache, SRUM.",
                    "Análisis de memoria RAM con Volatility 3: plugins `windows.pslist`, `windows.malfind`, `windows.netscan`.",
                ],
                exam_tips=[
                    "Los archivos Prefetch en `C:\\Windows\\Prefetch` confirman que un ejecutable corrió en la máquina y guardan la hora exacta de ejecución.",
                ],
                recommended_labs=[
                    "TryHackMe: KAPE Room (Free)",
                    "TryHackMe: Volatility (Free)",
                ],
                free_resources=[
                    {"name": "Eric Zimmerman's Forensic Tools", "url": "https://ericzimmerman.github.io/"},
                ],
            ),
        ],
    ),

    "pjpt": CertificationInfo(
        cert_id="pjpt",
        name="Practical Junior Penetration Tester (PJPT)",
        vendor="TCM Security",
        level="Práctico Ofensivo / Active Directory",
        exam_format="Examen práctico de 48 horas en entorno interno de Active Directory + 48h para redacción de informe",
        passing_score="Compromiso total del Domain Controller (DC) y reporte profesional",
        passing_percentage=100.0,
        description="Enfocado en pentesting de redes corporativas y Active Directory interno (LLMNR poisoning, Kerberoasting, pivoting y elevación a Domain Admin).",
        official_url="https://certifications.tcm-sec.com/pjpt/",
        aliases=["pjpt", "tcm pjpt", "practical junior penetration tester", "pjpt ad"],
        domains=[
            {"name": "OSINT & External Information Gathering", "weight": "20%"},
            {"name": "Initial Internal Access & Credential Harvesting", "weight": "25%"},
            {"name": "Active Directory Exploitation (Kerberoasting, AS-REP)", "weight": "35%"},
            {"name": "Post-Exploitation & Professional Reporting", "weight": "20%"},
        ],
        study_topics=[
            StudyTopic(
                domain="OSINT & External Information Gathering",
                title="Inteligencia de Fuentes Abiertas y Búsqueda de Credenciales",
                concepts=[
                    "Búsqueda de fugas de credenciales en GitHub, Pastebin, DeHashed.",
                    "Enumeración de usuarios con Hunter.io, LinkedIn y Phonebook.cz para armar listas de nombres de usuario.",
                    "Enumeración pasiva de subdominios y tecnologías expuestas.",
                ],
                exam_tips=[
                    "En los exámenes de TCM Security, los repositorios de GitHub de la empresa ficticia suelen contener credenciales de prueba o llaves de API olvidadas.",
                ],
                recommended_labs=[
                    "TryHackMe: Google Dorking & OSINT (Free)",
                ],
                free_resources=[
                    {"name": "OSINT Framework", "url": "https://osintframework.com/"},
                ],
            ),
            StudyTopic(
                domain="Initial Internal Access & Credential Harvesting",
                title="Captura de Hashes y Password Spraying",
                concepts=[
                    "LLMNR/NBT-NS Poisoning con Responder en interfaces internas.",
                    "Captura de hashes NetNTLMv2 y crackeo con Hashcat (modo 5600) usando `rockyou.txt`.",
                    "Password Spraying metódico respetando políticas de bloqueo de cuenta (Account Lockout Threshold).",
                ],
                exam_tips=[
                    "Nunca pruebes contraseñas al azar contra AD para no bloquear cuentas. El password spray prueba una sola clave común (ej. `SeasonYear!`) espaciada en el tiempo.",
                ],
                recommended_labs=[
                    "TryHackMe: Password Attacks (Free)",
                ],
                free_resources=[
                    {"name": "NetExec (nxc) Documentation", "url": "https://www.netexec.org/"},
                ],
            ),
            StudyTopic(
                domain="Active Directory Exploitation",
                title="Vectores Clásicos contra Active Directory",
                concepts=[
                    "AS-REP Roasting: Cuentas sin preautenticación Kerberos requerida (`DONT_REQ_PREAUTH`).",
                    "Kerberoasting: Solicitar tickets TGS para cuentas de servicio con SPNs registrados y crackear el hash offline con Hashcat (modo 13100).",
                    "Enumeración con BloodHound / SharpHound para graficar rutas de ataque hacia Domain Admin.",
                ],
                exam_tips=[
                    "TCM valora el reporte tanto como la explotación. Anota cada comando, captura de pantalla y recomendación de remediación conforme avanzas.",
                ],
                recommended_labs=[
                    "TryHackMe: Attacktive Directory (Free)",
                ],
                free_resources=[
                    {"name": "The Practical Ethical Hacking Guide (Heath Adams)", "url": "https://tcm-sec.com/"},
                ],
            ),
            StudyTopic(
                domain="Post-Exploitation & Professional Reporting",
                title="Extracción de NTDS.dit y Elaboración de Informes Profesionales",
                concepts=[
                    "Dumping de la base de datos de AD: `secretsdump.py` mediante DRSUAPI o VSS (Volume Shadow Copy).",
                    "Estructura del informe: Resumen Ejecutivo, Clasificación de Hallazgos por CVSS, Pasos de Reproducción Detallados y Remediaciones.",
                ],
                exam_tips=[
                    "Para aprobar PJPT debes entregar un informe completo que un directivo no técnico pueda comprender junto con la solución técnica precisa.",
                ],
                recommended_labs=[
                    "TCM Security: Sample Pentest Report",
                ],
                free_resources=[
                    {"name": "TCM Pentest Report Template", "url": "https://github.com/hma0/tcm-security-pentest-report-template"},
                ],
            ),
        ],
    ),

    "btl1": CertificationInfo(
        cert_id="btl1",
        name="Blue Team Level 1 (BTL1)",
        vendor="Security Blue Team",
        level="Práctico Operacional Blue Team",
        exam_format="Examen de investigación de incidente de 24 horas en máquina virtual dedicada con 20 preguntas basadas en evidencias",
        passing_score="70% (con medalla de oro si se supera el 90% en primer intento)",
        passing_percentage=70.0,
        description="Certificación defensiva británica de gran prestigio. Cubre análisis de phishing, inteligencia de amenazas, SIEM (Splunk), forense digital y análisis de red.",
        official_url="https://www.securityblue.team/certifications/blue-team-level-1",
        aliases=["btl1", "btl-1", "blue team level 1", "security blue team"],
        domains=[
            {"name": "Phishing Analysis", "weight": "20%"},
            {"name": "Threat Intelligence (OSINT & MITRE)", "weight": "15%"},
            {"name": "Digital Forensics & Artifact Analysis", "weight": "25%"},
            {"name": "SIEM (Splunk)", "weight": "20%"},
            {"name": "Network Analysis & Incident Response", "weight": "20%"},
        ],
        study_topics=[
            StudyTopic(
                domain="Phishing Analysis",
                title="Inspección Forense de Correos y Adjuntos Maliciosos",
                concepts=[
                    "Cabeceras de correo: Análisis de `Received: from`, `Return-Path` y autenticación SPF, DKIM y DMARC.",
                    "Análisis de archivos `.eml` y `.msg`.",
                    "Extracción de URLs sospechosas, ofuscación en enlaces y análisis de adjuntos en sandbox seguro (Any.Run, VirusTotal).",
                ],
                exam_tips=[
                    "En phishing, el campo 'From:' puede falsificarse fácilmente; la IP real del servidor remitente siempre se encuentra en la cabecera 'Received:' más baja cronológicamente.",
                ],
                recommended_labs=[
                    "TryHackMe: Phishing Emails 1 & 2 (Free)",
                ],
                free_resources=[
                    {"name": "Cisco Talos Reputation Lookup", "url": "https://talosintelligence.com/"},
                ],
            ),
            StudyTopic(
                domain="Threat Intelligence (OSINT & MITRE)",
                title="Inteligencia de Amenazas y Clasificación de Actores CTI",
                concepts=[
                    "Ciclo de Inteligencia: Dirección, Recolección, Procesamiento, Análisis y Difusión.",
                    "Modelo Diamond de Análisis de Intrusiones: Adversario, Capacidad, Infraestructura y Víctima.",
                    "Plataformas MISP (Malware Information Sharing Platform) y feeds de IOCs.",
                ],
                exam_tips=[
                    "El Modelo Diamond ayuda a correlacionar eventos conectando los 4 vértices para entender la campaña del adversario.",
                ],
                recommended_labs=[
                    "TryHackMe: MISP Room (Free)",
                ],
                free_resources=[
                    {"name": "Diamond Model of Intrusion Analysis PDF", "url": "https://www.activeresponse.org/wp-content/uploads/2013/07/diamond_onsite.pdf"},
                ],
            ),
            StudyTopic(
                domain="Digital Forensics & Artifact Analysis",
                title="Forense Digital de Disco y Análisis de Artefactos",
                concepts=[
                    "Cadena de Custodia e Hashing de imágenes forenses (E01, RAW/DD).",
                    "Artefactos clave: LNK files, Jump Lists, Shellbags para reconstruir acceso a carpetas.",
                    "Análisis de MFT ($MFT / Master File Table) y Resident vs Non-Resident data.",
                ],
                exam_tips=[
                    "Los Shellbags demuestran la existencia de una carpeta y que el usuario navegó por ella, incluso si la carpeta fue borrada después.",
                ],
                recommended_labs=[
                    "TryHackMe: Windows Forensics 1 & 2 (Free)",
                ],
                free_resources=[
                    {"name": "SANS Digital Forensics Posters", "url": "https://www.sans.org/posters/"},
                ],
            ),
            StudyTopic(
                domain="SIEM (Splunk)",
                title="Investigación y Búsqueda Avanzada en Splunk (SPL)",
                concepts=[
                    "Comandos SPL esenciales: `index=* sourcetype=* | stats count by user`, `eval`, `rex`, `lookup`, `transaction`.",
                    "Cálculo de valores atípicos y rare searching (`rare field`).",
                    "Construcción de dashboards de alerta y playbooks de investigación.",
                ],
                exam_tips=[
                    "En BTL1, la velocidad para filtrar por ventanas de tiempo (`earliest` y `latest`) y agregar con `stats count` es determinante.",
                ],
                recommended_labs=[
                    "TryHackMe: Investigating with Splunk (Free)",
                ],
                free_resources=[
                    {"name": "Splunk Search Reference Manual", "url": "https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Whatsinthismanual"},
                ],
            ),
            StudyTopic(
                domain="Network Analysis & Incident Response",
                title="Análisis de Red y Respuesta Táctica a Incidentes",
                concepts=[
                    "Inspección de flujos TCP/IP, detección de exfiltración de datos por DNS Tunneling.",
                    "Análisis de logs de proxies web y categorización de tráfico malicioso.",
                    "Aislamiento de hosts comprometidos y contención de amenazas en vivo.",
                ],
                exam_tips=[
                    "Si observas consultas DNS con subdominios anormalmente largos en base64 (ej. `aHR0cHM6...attacker.com`), se trata de DNS Exfiltration/Tunneling.",
                ],
                recommended_labs=[
                    "TryHackMe: Network Forensics (Free)",
                ],
                free_resources=[
                    {"name": "Wireshark User's Guide", "url": "https://www.wireshark.org/docs/wsug_html_chunked/"},
                ],
            ),
        ],
    ),

    "ceh": CertificationInfo(
        cert_id="ceh",
        name="Certified Ethical Hacker (CEH v12)",
        vendor="EC-Council",
        level="Intermediate (Certificación Clásica de la Industria)",
        exam_format="125 preguntas de opción múltiple (4 horas)",
        passing_score="Entre 70% y 85% dependiendo del banco de preguntas dinámico",
        passing_percentage=75.0,
        description="Certificación clásica de hacking ético de EC-Council enfocada en metodología exhaustiva de auditoría, herramientas estándar y vectores de intrusión.",
        official_url="https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/",
        aliases=["ceh", "cehv12", "ceh v12", "certified ethical hacker", "eccouncil ceh"],
        domains=[
            {"name": "Information Security and Ethical Hacking Overview", "weight": "6%"},
            {"name": "Reconnaissance Techniques", "weight": "21%"},
            {"name": "System Hacking Phases and Attack Techniques", "weight": "17%"},
            {"name": "Network and Perimeter Hacking", "weight": "14%"},
            {"name": "Web Application and Mobile Hacking", "weight": "16%"},
            {"name": "Wireless and Cloud Security", "weight": "12%"},
            {"name": "Cryptography and Security Controls", "weight": "14%"},
        ],
        study_topics=[
            StudyTopic(
                domain="Reconnaissance & Scanning",
                title="Técnicas de Escaneo y Banderas de Herramientas Clásicas",
                concepts=[
                    "Tipos de escaneos Nmap: SYN Stealth (`-sS`), TCP Connect (`-sT`), NULL scan (`-sN`), FIN scan (`-sF`), Xmas scan (`-sX`).",
                    "Comportamiento de paquetes en escaneo Xmas: Activa las banderas FIN, URG y PSH (como un 'árbol de navidad iluminado').",
                    "Evasión de IDS/Firewall: Fragmentación de paquetes (`-f`), señuelos (`-D RND:10`), spoofing de dirección origen (`-S`).",
                ],
                exam_tips=[
                    "El examen CEH pregunta con frecuencia por nombres exactos de herramientas clásicas y combinaciones de banderas de Nmap, Hping3 y John the Ripper.",
                ],
                recommended_labs=[
                    "TryHackMe: Nmap Room (Free)",
                ],
                free_resources=[
                    {"name": "Nmap Official Reference Guide", "url": "https://nmap.org/book/man.html"},
                ],
            ),
            StudyTopic(
                domain="System Hacking Phases and Attack Techniques",
                title="Fases de Intrusión en Sistemas y Crackeo de Credenciales",
                concepts=[
                    "Fases: Ganar Acceso, Escalar Privilegios, Mantener Acceso (Backdoors/Rootkits), Ocultar Huellas (Borrado de logs de eventos).",
                    "Ataques a contraseñas: Diccionario, Fuerza Bruta, Tablas Rainbow (con hashes precalculados) y Salts.",
                    "Esteganografía: Ocultar mensajes dentro de imágenes (Least Significant Bit - LSB) con herramientas como OpenStego o Steghide.",
                ],
                exam_tips=[
                    "Una Tabla Rainbow almacena cadenas de reducción de contraseñas precomputadas; el uso de una 'Salt' criptográfica aleatoria anula completamente su efectividad.",
                ],
                recommended_labs=[
                    "TryHackMe: John the Ripper & Hydra (Free)",
                ],
                free_resources=[
                    {"name": "Hashcat Official Documentation", "url": "https://hashcat.net/wiki/"},
                ],
            ),
            StudyTopic(
                domain="Network and Perimeter Hacking",
                title="Ataques a Perímetros de Red, Sniffing y Denegación de Servicio",
                concepts=[
                    "Sniffing activo: Envenenamiento de caché ARP (arpspoof/Ettercap), inundación de tablas MAC (MAC Flooding con macof).",
                    "Ataques DoS/DDoS: SYN Flood, Smurf Attack (amplificación ICMP mediante dirección broadcast), Ping of Death.",
                    "Secuestro de sesión (Session Hijacking): Predicción de números de secuencia TCP y fijación de sesión.",
                ],
                exam_tips=[
                    "En MAC Flooding, el switch agota la memoria CAM y conmuta a modo 'Hub', difundiendo todo el tráfico por todos los puertos para permitir el sniffing.",
                ],
                recommended_labs=[
                    "TryHackMe: Network Attacks (Free)",
                ],
                free_resources=[
                    {"name": "Wireshark Packet Analysis", "url": "https://www.wireshark.org/"},
                ],
            ),
            StudyTopic(
                domain="Web Application and Mobile Hacking",
                title="Vulnerabilidades Web OWASP y Amenazas en Entornos Móviles",
                concepts=[
                    "OWASP Top 10: Inyecciones (SQLi, NoSQLi), Fallos Criptográficos, Control de Acceso Roto, SSRF.",
                    "Ataques a APIs RESTful: Manipulación de tokens JWT (algoritmo 'none', firmas débiles).",
                    "Seguridad en dispositivos móviles: Sandboxing de Android vs iOS, permisos en AndroidManifest.xml.",
                ],
                exam_tips=[
                    "En JWT, cambiar el encabezado a `\"alg\": \"none\"` para burlar la verificación de firma es una pregunta clásica en exámenes de seguridad de aplicaciones.",
                ],
                recommended_labs=[
                    "PortSwigger Web Security Academy (Free)",
                ],
                free_resources=[
                    {"name": "OWASP Top 10 Official Document", "url": "https://owasp.org/Top10/"},
                ],
            ),
        ],
    ),
}


def list_all_certifications() -> List[CertificationInfo]:
    """Devuelve la lista ordenada de todas las certificaciones registradas en el catálogo."""
    return list(CERTIFICATION_CATALOG.values())


def get_cert_by_name_or_alias(query: str) -> Optional[CertificationInfo]:
    """
    Busca y resuelve una certificación por su ID directo, número de catálogo (1..N) o alias común.
    Ejemplos: '1', 'isc2', 'cc', 'sec+', 'security+', 'ejpt', 'cjca', 'btl1'.
    """
    cleaned = query.strip().lower()
    if not cleaned:
        return None

    # Búsqueda por índice numérico (1..N)
    all_certs = list_all_certifications()
    if cleaned.isdigit():
        idx = int(cleaned) - 1
        if 0 <= idx < len(all_certs):
            return all_certs[idx]

    # Búsqueda exacta por cert_id
    if cleaned in CERTIFICATION_CATALOG:
        return CERTIFICATION_CATALOG[cleaned]

    # Búsqueda por alias
    for cert in all_certs:
        if cleaned in [a.lower() for a in cert.aliases]:
            return cert

    # Búsqueda parcial por subcadena en nombre
    for cert in all_certs:
        if cleaned in cert.name.lower() or cleaned in cert.cert_id.lower():
            return cert

    return None
