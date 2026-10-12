# 🛡️ CTF-AI Solver Pro — Autonomous CTF Agent & Cybersecurity Study Mentor

> **Plataforma Integral en Terminal para Resolución Autónoma de Retos CTF y Formación Avanzada en Ciberseguridad**  
> Conecta modelos de IA de última generación (Google Gemini con SDK oficial `google-genai`, OpenAI y Claude) con un motor de razonamiento basado en evidencias de 13 pasos, herramientas de análisis forense, criptografía, reversing y web, sandboxing local de ejecución y un mentor socrático de estudio personalizado.

---

## ⚡ Novedades en CTF-AI Solver Pro

1. **🧠 Motor Autónomo de Resolución Basado en Evidencias (13 Pasos)**:
   - Ciclo científico riguroso: *Enunciado ➔ Clasificación ➔ Inventario ➔ Hipótesis ➔ Plan Priorizado ➔ Herramienta Estructurada ➔ Hechos Observados ➔ Actualización de Hipótesis ➔ Replanificación ante fallos ➔ Banderas Candidatas ➔ Validación contra Evidencias ➔ Reporte Reproducible*.
   - Previene alucinaciones distinguiendo formalmente entre hipótesis, datos empíricos y flags verificadas.
2. **🧰 Arsenal de Herramientas Estructuradas (`BaseTool` & `ToolRegistry`)**:
   - **Criptografía**: MultiDecoder recursivo (Base64, Hex, URL, ROT13), análisis de entropía de Shannon e Índice de Coincidencia (IoC), ataques RSA (`small e = 3` raíz cúbica exacta y factorización de Fermat).
   - **Forense Digital**: Inspección de Magic Bytes (30+ firmas binarias), extracción profunda de cadenas (`DeepStrings` ASCII y UTF-16 LE/BE), inspección segura de archivos ZIP (protección contra zip-bombs y path traversal), y analizador nativo de capturas de red PCAP en Python puro sin dependencias externas.
   - **Ingeniería Inversa**: Parser de cabeceras ejecutables ELF (Linux) y PE (Windows), cálculo de entropía por secciones para detección de empaquetadores (UPX/ofuscación) y comprobación de herramientas del sistema.
   - **Web & Redes**: Auditoría de cabeceras de seguridad HTTP y cookies, escáner estático de secretos (API keys, AWS, tokens JWT, endpoints en HTML/JS), Scope Enforcer estricto para evitar peticiones no autorizadas, y análisis de resolución DNS.
3. **🔒 Aislamiento y Sandboxing de Ejecución**:
   - Detección automática del demonio de Docker con fallback transparente al sandbox local por workspace (`workspaces/<id>`).
   - Confinamiento estricto de rutas contra intentos de Path Traversal (`../`).
   - Depuración de variables de entorno sensibles (elimina API keys del subproceso).
   - Filtro de seguridad heurístico contra *Prompt Injections* en archivos o textos analizados.
4. **🎓 Cybersecurity Study Mentor & Preparación de Certificaciones**:
   - **Preparación Oficial de Certificaciones (`cert` / `/cert`)**: Itinerarios completos con temas de estudio, blueprints ponderados, tips de examen, laboratorios recomendados y recursos oficiales para **ISC2 CC**, **CompTIA Security+**, **CompTIA Network+**, **eJPT v2**, **CJCA**, **PJPT**, **BTL1** y **CEH**.
   - **Simulacros de Examen y Quizzes Interactivos (`quiz [cert]`)**: Banco curado offline con escenarios de examen reales, modo híbrido con IA, retroalimentación inmediata y diagnóstico detallado de dominios fuertes y áreas a reforzar.
   - Entrevista de diagnóstico formativo (`mentor` / `study`).
   - Generación de rutas personalizadas por semanas y módulos (`roadmap` / `rm`).
   - Catálogo curado de plataformas 100% legítimas y gratuitas (PortSwigger, OverTheWire Bandit, TryHackMe, Cisco Networking Academy, Linux Journey, OWASP).
   - Recalibración dinámica del cronograma semanal (`plan-study <horas>`).
5. **📊 Informes Técnicos Reproducibles**:
   - Exportación de writeups profesionales en Markdown detallando metodología, evidencias confirmadas, herramientas ejecutadas y conclusión (`report`).

---

## 🚀 Instalación y Puesta en Marcha

### Requisitos Previos
- **Windows 10 / 11** con **PowerShell 5.1** o **PowerShell 7+** (o Linux / macOS)
- **Python 3.10** o superior instalado en el sistema

### 1. Clonar el Repositorio
```powershell
git clone https://github.com/tu-usuario/ctf-ai-solver.git
cd ctf-ai-solver
```

### 2. Configurar Claves de API en `.env`
Copia la plantilla `.env.example` y edita tu archivo `.env`:
```powershell
Copy-Item .env.example .env
```

Contenido del archivo `.env`:
```ini
# Google Gemini (Gratuito en Google AI Studio - https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=tu_clave_gemini_aqui

# OpenAI (Opcional - https://platform.openai.com/api-keys)
OPENAI_API_KEY=tu_clave_openai_aqui

# Anthropic Claude (Opcional - https://console.anthropic.com/)
ANTHROPIC_API_KEY=tu_clave_claude_aqui

# Proveedor por defecto: gemini, openai, claude
DEFAULT_PROVIDER=gemini
```

### 3. Iniciar el Asistente
Ejecuta el script PowerShell launcher (creará automáticamente el entorno virtual `venv` e instalará dependencias):
```powershell
.\ctf-ai.ps1
```
*(O de forma directa: `python -m venv venv`, `.\venv\Scripts\pip install -r requirements.txt`, `python main.py`)*

---

## 🕹️ Guía de Comandos

### Ciclo Autónomo y Retos CTF
| Comando | Alias | Descripción |
|---|---|---|
| `challenge <texto>` | `c` | Define el enunciado del reto y genera la hipótesis inicial |
| `file <ruta>` | `f` | Adjunta un archivo para análisis binario, forense o strings |
| `solve` | `s` | Inicia el bucle de razonamiento y ejecución autónomo |
| `step` | `st` | Ejecuta un único paso táctico del plan |
| `evidence` | `evd` | Inspecciona el inventario de evidencias, hechos y flags candidatas |
| `plan` | `pl` | Muestra el árbol de tareas, prioridades y consumo de presupuesto |
| `report [ruta]` | `rep` | Exporta un informe técnico completo del reto a Markdown |

### Interacción Asistida y Utilidades
| Comando | Alias | Descripción |
|---|---|---|
| `ask <pregunta>` | `a` | Consulta libremente a la IA sobre técnicas, vulnerabilidades o conceptos |
| `tool <nombre> [args]` | `t` | Ejecuta utilidades integradas directas (`b64d`, `hexd`, `rot13`, `caesar`, `hashid`, etc.) |
| `exec <comando>` | `!` | Ejecuta un comando en la consola del sistema con confirmación interactiva |
| `provider <nombre>` | `p` | Alterna entre proveedores de IA (`gemini`, `openai`, `claude`) |
| `context` | `ctx` | Muestra el resumen del estado acumulado de la sesión |
| `save [archivo]` | | Guarda la sesión completa en formato JSON |
| `load [archivo]` | | Restaura una sesión previamente guardada |
| `diag` | `diagnostics` | Comprueba el estado de la conexión a APIs, Docker y herramientas en PATH |

### Certificaciones & Cybersecurity Study Mentor
| Comando | Alias | Descripción |
|---|---|---|
| `cert [nombre/num]` | `certs` | Abre el catálogo o el plan de preparación temática para una certificación (ISC2, Sec+, eJPT, etc.) |
| `quiz [cert/tema]` | `qz`, `exam` | Inicia un simulacro interactivo de examen con puntuación oficial y diagnóstico por dominios |
| `mentor [consulta]` | `study` | Asesoría pedagógica con el mentor IA sobre cursos, cupones gratis y rutas |
| `roadmap [rol]` | `rm` | Muestra o regenera tu ruta formativa personalizada por módulos semanales |
| `plan-study <horas>` | `schedule` | Recalibra el cronograma si tus horas semanales disponibles cambian |
| `open <nº>` | `o` | Abre cualquier curso o enlace web de inmediato en tu navegador predeterminado |

---

## 🧪 Ejecución de la Suite de Pruebas

El proyecto cuenta con una batería completa de pruebas unitarias y de integración que no requieren dependencias externas activas:

```powershell
# Ejecutar todas las pruebas unitarias
& ".\venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py"

# Ejecutar test de conexión real con Gemini y verificación segura de credenciales
& ".\venv\Scripts\python.exe" tests\test_gemini_connection.py
```

## Cisco Packet Tracer autónomo

El flujo de Packet Tracer está integrado como un caso de uso separado de los
retos CTF:

```powershell
pt capabilities
pt solve "C:\ruta\practica.pdf" "C:\ruta\resultado.pkt"
pt pause
pt resume
pt stop
```

El analizador combina texto y varios PDF, genera un `NetworkBlueprint`,
valida direccionamiento, subredes, interfaces y enlaces, y después delega las
operaciones al adaptador disponible. Las respuestas del adaptador deben
confirmar cada operación; un comando enviado sin respuesta positiva no se
considera aplicado.

Packet Tracer 9 instalado localmente incluye la documentación oficial de IPC y
PTMP. El detector comprueba el ejecutable, la documentación y el listener TCP
39000 por defecto, pero un puerto abierto no se presenta como una operación IPC
autenticada. El puente Socket.IO en 7531 es opcional y externo: solo habilita
edición cuando una extensión compatible se conecta y devuelve resultados reales.
Sin esa conexión, el agente no simula creación de dispositivos, cableado,
configuración ni pings.
