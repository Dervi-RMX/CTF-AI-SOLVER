"""
Banco Curado de Preguntas de Examen de Práctica para Certificaciones de Ciberseguridad.
Contiene escenarios realistas tipo examen, opciones múltiples (A, B, C, D),
claves de respuesta correctas y explicaciones pedagógicas exhaustivas para cada dominio oficial.
"""

from typing import Any, Dict, List

CERT_QUESTION_BANK: List[Dict[str, Any]] = [
    # =========================================================================
    # ISC2 CC (Certified in Cybersecurity)
    # =========================================================================
    {
        "cert_id": "isc2_cc",
        "domain": "Domain 1: Security Principles",
        "scenario": "Una empresa financiera sufre una alteración no autorizada en su base de datos de saldos bancarios debido a un fallo en un script interno.",
        "question": "¿Qué pilar fundamental de la Tríada CIA se ha visto directamente comprometido en este incidente?",
        "options": [
            "A) Confidencialidad",
            "B) Integridad",
            "C) Disponibilidad",
            "D) No Repudio",
        ],
        "answer": "B",
        "explanation": "La Integridad garantiza que la información sea exacta, completa y que no haya sido modificada o borrada sin autorización. La alteración de los saldos bancarios viola directamente la integridad de los datos.",
    },
    {
        "cert_id": "isc2_cc",
        "domain": "Domain 3: Access Controls Concepts",
        "scenario": "Un administrador de red implementa un nuevo sistema donde los usuarios deben ingresar su contraseña de dominio y luego pulsar una llave criptográfica física USB (FIDO2).",
        "question": "¿Qué categoría de autenticación representa esta implementación según las mejores prácticas de seguridad?",
        "options": [
            "A) Autenticación de Factor Único mediante doble secreto conocido.",
            "B) Autenticación Multifactor (MFA) combinando 'Algo que sabes' con 'Algo que tienes'.",
            "C) Control de Acceso Discrecional (DAC) basado en jerarquías.",
            "D) Autenticación Biométrica Federada de alta densidad.",
        ],
        "answer": "B",
        "explanation": "La contraseña representa 'algo que sabes' y la llave física FIDO2 representa 'algo que tienes'. Al combinar dos factores de categorías distintas, se cumple estrictamente la definición de Autenticación Multifactor (MFA).",
    },
    {
        "cert_id": "isc2_cc",
        "domain": "Domain 2: Incident Response, BC & DR",
        "scenario": "Durante la planificación de contingencia de una corporación, la junta directiva determina que los sistemas críticos no pueden permanecer inactivos por más de 4 horas en caso de catástrofe.",
        "question": "¿Qué métrica oficial de Continuidad del Negocio y Recuperación ante Desastres (DRP) define este parámetro?",
        "options": [
            "A) RPO (Recovery Point Objective)",
            "B) RTO (Recovery Time Objective)",
            "C) MTBF (Mean Time Between Failures)",
            "D) SLA (Service Level Agreement)",
        ],
        "answer": "B",
        "explanation": "El RTO (Recovery Time Objective) es la cantidad máxima de tiempo tolerable que una organización puede esperar antes de restaurar un proceso de negocio o sistema. El RPO mide la pérdida máxima admisible de datos en tiempo transaccional.",
    },
    {
        "cert_id": "isc2_cc",
        "domain": "Domain 4: Network Security",
        "scenario": "Un analista necesita monitorizar el tráfico de red perimetral para detectar posibles intrusiones y bloquear automáticamente cualquier flujo malicioso en tiempo real.",
        "question": "¿Qué dispositivo o tecnología debe desplegarse en la topología para cumplir este requisito?",
        "options": [
            "A) NIDS (Network Intrusion Detection System) en modo promiscuo a través de un puerto SPAN.",
            "B) NIPS (Network Intrusion Prevention System) colocado en línea (in-line) en el flujo de paquetes.",
            "C) Servidor proxy inverso configurado únicamente con balanceo Round-Robin.",
            "D) Switch de capa 2 sin soporte VLAN.",
        ],
        "answer": "B",
        "explanation": "Un NIPS se coloca 'in-line' (en línea) con el tráfico para poder inspeccionar los paquetes y tomar acciones activas inmediatas como descartarlos (drop) o resetear la conexión TCP. Un NIDS es meramente pasivo y solo genera alertas.",
    },
    {
        "cert_id": "isc2_cc",
        "domain": "Domain 5: Security Operations",
        "scenario": "Un hospital planea retirar del servicio varios servidores antiguos que almacenaban historiales clínicos de pacientes en discos duros mecánicos.",
        "question": "¿Cuál es el método más seguro y definitivo para garantizar que la información confidencial sea irrecuperable antes del reciclaje?",
        "options": [
            "A) Realizar un formateo rápido desde el sistema operativo Windows Server.",
            "B) Eliminar la tabla de particiones y crear un nuevo volumen NTFS.",
            "C) Desmagnetización completa (Degaussing) o destrucción física mediante trituración mecánica (Shredding).",
            "D) Reinstalar el sistema operativo base sin conectar los discos a la red.",
        ],
        "answer": "C",
        "explanation": "El formateo o borrado de particiones deja los datos accesibles mediante herramientas forenses estándar. La destrucción física (shredding/incineración) o el degaussing (desmagnetización electromagnética) son los únicos métodos recomendados por estándares como NIST SP 800-88 para datos médicos críticos.",
    },

    # =========================================================================
    # CompTIA Security+ (SY0-701)
    # =========================================================================
    {
        "cert_id": "comptia_secplus",
        "domain": "1.0 General Security Concepts",
        "scenario": "Una organización adopta un modelo de seguridad donde ninguna solicitud de acceso a recursos internos es confiable de forma predeterminada, requiriendo autenticación e inspección continua de contexto, ubicación y postura del dispositivo.",
        "question": "¿Qué principio y arquitectura de seguridad describe exactamente esta estrategia?",
        "options": [
            "A) Seguridad Perimetral Tradicional de 'Castillo y Foso' (Castle-and-Moat).",
            "B) Arquitectura Zero Trust (ZTA - Zero Trust Architecture).",
            "C) Aislamiento mediante DMZ única sin microsegmentación.",
            "D) Control de Acceso Discrecional Abierto (Open DAC).",
        ],
        "answer": "B",
        "explanation": "La Arquitectura Zero Trust (ZTA) parte de la premisa de que las amenazas existen tanto dentro como fuera de la red perimetral, aplicando verificación explícita, mínimo privilegio y asumiendo brecha de seguridad en todo momento.",
    },
    {
        "cert_id": "comptia_secplus",
        "domain": "2.0 Threats, Vulnerabilities & Mitigations",
        "scenario": "Un atacante envía correos electrónicos altamente personalizados al Director Financiero (CFO) simulando ser el CEO de la compañía y solicitando una transferencia urgente de fondos para una adquisición confidencial.",
        "question": "¿Qué tipo específico de técnica de ingeniería social se está ejecutando?",
        "options": [
            "A) Phishing Masivo (Bulk Phishing)",
            "B) Whaling (Caza de Ballenas)",
            "C) Vishing Telefónico",
            "D) Shoulder Surfing",
        ],
        "answer": "B",
        "explanation": "El Whaling es una variante altamente dirigida de spear phishing orientada específicamente a directivos de alto nivel ejecutivo (C-level, directores financieros, directores generales) debido a su acceso a fondos o información confidencial.",
    },
    {
        "cert_id": "comptia_secplus",
        "domain": "4.0 Security Operations",
        "scenario": "Durante una investigación forense digital tras una brecha de seguridad activa en un servidor comprometido, el equipo debe recopilar evidencias cumpliendo con el orden de volatilidad de la RFC 3227.",
        "question": "¿Cuál de los siguientes artefactos debe ser adquirido en primer lugar por el perito forense?",
        "options": [
            "A) Volcado del disco duro principal (SATA SSD)",
            "B) Contenido de la memoria RAM y registros del procesador / caché",
            "C) Copias de seguridad almacenadas en cintas externas",
            "D) Registros de logs guardados en el SIEM centralizado",
        ],
        "answer": "B",
        "explanation": "Según el Orden de Volatilidad (RFC 3227), la evidencia más efímera debe capturarse primero: Registros de CPU/Caché -> Memoria RAM -> Estado de conexiones de red -> Almacenamiento en disco -> Medios de backup.",
    },
    {
        "cert_id": "comptia_secplus",
        "domain": "2.0 Threats, Vulnerabilities & Mitigations",
        "scenario": "Al auditar los logs de un servidor web Apache, un analista observa la siguiente petición HTTP: 'GET /search?q=1%27%20UNION%20SELECT%20username,%20password%20FROM%20users-- HTTP/1.1'.",
        "question": "¿Qué vulnerabilidad web está intentando explotar el atacante?",
        "options": [
            "A) Cross-Site Scripting (XSS) Almacenado",
            "B) Inyección SQL basada en Uniones (UNION-based SQL Injection)",
            "C) Server-Side Request Forgery (SSRF)",
            "D) Inyección de Comandos del Sistema Operativo",
        ],
        "answer": "B",
        "explanation": "El payload utiliza la sintaxis 'UNION SELECT' para concatenar los resultados de la consulta original con registros extraídos de la tabla interna 'users', característica distintiva de una inyección SQL.",
    },

    # =========================================================================
    # CompTIA Network+ (N10-008)
    # =========================================================================
    {
        "cert_id": "comptia_netplus",
        "domain": "1.0 Networking Fundamentals",
        "scenario": "Una estación de trabajo recién encendida en una oficina no logra navegar por Internet. Al ejecutar 'ipconfig', el técnico observa la dirección IP 169.254.12.89 con máscara 255.255.0.0.",
        "question": "¿Cuál es la causa más probable de esta asignación de dirección?",
        "options": [
            "A) El servidor DNS rechazó la resolución de nombres FQDN.",
            "B) El cliente no pudo contactar con un servidor DHCP y asignó una dirección APIPA (Automatic Private IP Addressing).",
            "C) La tarjeta de red está configurada en modo promiscuo de captura.",
            "D) El router habilitó automáticamente una subred RFC 1918 de clase A.",
        ],
        "answer": "B",
        "explanation": "El rango 169.254.0.0/16 está reservado para APIPA (IPv4 Link-Local). Ocurre de forma automática cuando el cliente envía solicitudes DHCP Discover y no recibe respuesta de ningún servidor DHCP.",
    },

    # =========================================================================
    # eJPT v2 (eLearnSecurity Junior Penetration Tester)
    # =========================================================================
    {
        "cert_id": "ejpt",
        "domain": "Host & Networking Auditing",
        "scenario": "Un pentester ejecuta un escaneo Nmap contra un servidor Linux de laboratorio y descubre el puerto 21/tcp abierto con el servicio vsftpd 2.3.4 y el script 'ftp-anon' reportando acceso permitido con usuario 'anonymous'.",
        "question": "¿Cuál debería ser el paso inmediato de enumeración del pentester?",
        "options": [
            "A) Lanzar un ataque de denegación de servicio SYN Flood contra el puerto 21.",
            "B) Iniciar sesión interactiva por FTP con credenciales 'anonymous:anonymous' y listar archivos o scripts legibles.",
            "C) Crackear inmediatamente los hashes del archivo /etc/shadow del servidor.",
            "D) Modificar las tablas de enrutamiento del kernel local.",
        ],
        "answer": "B",
        "explanation": "En la metodología de eJPT, el acceso anónimo FTP es un hallazgo crítico que debe explorarse de inmediato: suele albergar archivos de configuración, notas de administradores o respaldos que facilitan credenciales para otros servicios.",
    },
    {
        "cert_id": "ejpt",
        "domain": "Host & Networking Penetration Testing",
        "scenario": "Tras obtener una shell de bajos privilegios en un servidor Linux, el auditor ejecuta el comando 'find / -perm -4000 -type f 2>/dev/null' y localiza el binario '/usr/bin/python3' con el bit SUID activo perteneciente al usuario root.",
        "question": "¿Cómo puede el pentester escalar privilegios a root según el catálogo de GTFOBins?",
        "options": [
            "A) Ejecutar 'python3 -c \"import os; os.execl('/bin/sh', 'sh', '-p')\"'.",
            "B) Reiniciar el demonio de SSH mediante systemctl.",
            "C) Modificar el archivo hosts para redireccionar el tráfico local.",
            "D) Compilar un módulo de kernel en lenguaje Ensamblador.",
        ],
        "answer": "A",
        "explanation": "Cuando Python tiene permisos SUID (permiso octal 4000), puede invocar una shell preservando los privilegios efectivos de root mediante el flag `-p` de sh: `python3 -c \"import os; os.execl('/bin/sh', 'sh', '-p')\"`.",
    },
    {
        "cert_id": "ejpt",
        "domain": "Host & Networking Penetration Testing",
        "scenario": "El pentester compromete una máquina 'Pivote' que posee dos tarjetas de red: 'eth0' en 192.168.1.50 (red accesible) y 'eth1' en 10.10.10.5 (red interna no enrutable desde su máquina atacante).",
        "question": "¿Qué técnica y herramienta debe emplearse para poder escanear y atacar las máquinas de la subred 10.10.10.0/24 desde Kali Linux?",
        "options": [
            "A) Generar un túnel SOCKS mediante SSH / Chisel o Meterpreter AutoRoute y utilizar Proxychains.",
            "B) Desactivar el cortafuegos de Windows en la máquina del cliente.",
            "C) Cambiar la dirección MAC de la máquina atacante a una dirección de difusión (Broadcast).",
            "D) Ejecutar un ataque de Hombre en el Medio (MitM) vía Bluetooth.",
        ],
        "answer": "A",
        "explanation": "El pivoting permite utilizar una máquina comprometida como pasarela para acceder a redes internas aisladas mediante proxies dinámicos SOCKS (creados con SSH -D, Chisel o autoroute de Metasploit) y herramientas como Proxychains.",
    },

    # =========================================================================
    # CJCA (Certified Junior Cybersecurity Analyst)
    # =========================================================================
    {
        "cert_id": "cjca",
        "domain": "Network Architecture & Traffic Analysis",
        "scenario": "Analizando una captura Wireshark `.pcap` de una estación de trabajo sospechosa, el analista de SOC observa cientos de peticiones HTTP POST salientes hacia una IP desconocida en intervalos regulares de exactamente 60 segundos.",
        "question": "¿Qué patrón de comunicación maliciosa representa este comportamiento?",
        "options": [
            "A) Resolución inversa de DNS legítima.",
            "B) Beaconing de Comando y Control (C2 - Command & Control).",
            "C) Sincronización horaria estándar por protocolo NTP.",
            "D) Escaneo de puertos pasivo por TCP Connect.",
        ],
        "answer": "B",
        "explanation": "El 'Beaconing' es la señal periódica y regular que un malware (agente C2, como Cobalt Strike o Mythic) envía a su servidor de control para recibir nuevas órdenes o reportar estado.",
    },
    {
        "cert_id": "cjca",
        "domain": "Endpoint Security, SIEM & EDR",
        "scenario": "En los registros de Sysmon de una máquina de contabilidad, se registra el Event ID 1 (Process Creation) mostrando que el proceso padre 'WINWORD.EXE' ejecutó 'powershell.exe -NoP -NonI -W Hidden -Enc ...'.",
        "question": "¿Cuál es la deducción más precisa de este hallazgo en el triaje de incidentes?",
        "options": [
            "A) Un comportamiento normal del corrector ortográfico de Microsoft Word.",
            "B) Ejecución maliciosa originada por una macro o exploit embebido en un documento Word (Phishing/Malware).",
            "C) Una actualización automática del sistema operativo en segundo plano.",
            "D) Una copia de seguridad de archivos PST de Outlook.",
        ],
        "answer": "B",
        "explanation": "Microsoft Word (WINWORD.EXE) nunca debería invocar PowerShell con flags de ofuscación y ejecución oculta en condiciones legítimas. Esto indica la ejecución de una macro maliciosa de phishing que despliega un payload en memoria.",
    },

    # =========================================================================
    # PJPT (Practical Junior Penetration Tester)
    # =========================================================================
    {
        "cert_id": "pjpt",
        "domain": "Active Directory Exploitation",
        "scenario": "Durante un pentest interno en una red Active Directory corporativa, el evaluador ejecuta la herramienta Responder en su interfaz de red local.",
        "question": "¿Qué protocolos de resolución de nombres locales explota Responder para envenenar peticiones y capturar hashes NTLMv2?",
        "options": [
            "A) LLMNR (Link-Local Multicast Name Resolution) y NBT-NS (NetBIOS Name Service).",
            "B) BGP (Border Gateway Protocol) y RIP v2.",
            "C) SSHv2 y TLS 1.3.",
            "D) Kerberos PKINIT.",
        ],
        "answer": "A",
        "explanation": "Cuando un equipo Windows no logra resolver un nombre por DNS, recurre a LLMNR y NBT-NS por difusión local. Responder escucha estas peticiones, finge ser el servidor solicitado y fuerza al cliente a autenticarse, capturando el hash NetNTLMv2.",
    },

    # =========================================================================
    # BTL1 (Blue Team Level 1)
    # =========================================================================
    {
        "cert_id": "btl1",
        "domain": "Phishing Analysis",
        "scenario": "Al investigar un correo electrónico fraudulento reportado por un usuario, el analista defensivo necesita identificar la dirección IP real del servidor de correo que originó el mensaje.",
        "question": "¿Qué cabecera técnica del archivo `.eml` proporciona la fuente cronológicamente original del envío?",
        "options": [
            "A) La cabecera 'From:' que aparece en el cliente gráfico.",
            "B) La cabecera 'Received:' situada en la parte inferior de la cadena de retransmisión de saltos.",
            "C) El campo 'Subject:' del mensaje.",
            "D) La cabecera 'MIME-Version:'.",
        ],
        "answer": "B",
        "explanation": "El encabezado 'From:' puede falsificarse fácilmente. Cada servidor de correo legítimo que retransmite el mensaje añade una cabecera 'Received:' arriba de las anteriores; por lo tanto, la cabecera 'Received:' más baja (la primera registrada) revela la IP del remitente original.",
    },

    # =========================================================================
    # CEH (Certified Ethical Hacker)
    # =========================================================================
    {
        "cert_id": "ceh",
        "domain": "Reconnaissance & Scanning",
        "scenario": "Un auditor de seguridad ejecuta el comando 'nmap -sX 192.168.1.100' para evaluar la respuesta del stack TCP/IP del objetivo según la especificación RFC 793.",
        "question": "¿Qué banderas del encabezado TCP están activadas en los paquetes de sondeo de un escaneo Xmas (Navidad)?",
        "options": [
            "A) SYN, ACK y RST",
            "B) FIN, URG y PSH",
            "C) Únicamente la bandera SYN",
            "D) Todas las banderas en cero (NULL)",
        ],
        "answer": "B",
        "explanation": "El escaneo Xmas ('Árbol de Navidad') activa simultáneamente las banderas FIN, PSH y URG en el encabezado TCP. Según la RFC 793, si el puerto está cerrado devolverá un RST, y si está abierto no responderá nada en sistemas basados en UNIX.",
    },
]
