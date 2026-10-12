<#
.SYNOPSIS
    Launcher de PowerShell para CTF-AI Solver.
.DESCRIPTION
    Verifica los requisitos, inicializa el entorno virtual (venv), instala dependencias
    y ejecuta la herramienta con soporte para múltiples proveedores de IA.
.EXAMPLE
    .\ctf-ai.ps1
    .\ctf-ai.ps1 -p gemini
    .\ctf-ai.ps1 -c "Tengo un hash md5: 5d41402abc4b2a76b9719d911017c592"
#>

[CmdletBinding()]
param (
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

# Colores y encabezado
Write-Host ""
Write-Host " ================================================= " -ForegroundColor Cyan
Write-Host "   ⚡ CTF-AI Solver - Inicializador PowerShell ⚡   " -ForegroundColor Yellow
Write-Host " ================================================= " -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir

# 1. Comprobar si Python está instalado
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] No se encontró Python instalado en el sistema." -ForegroundColor Red
    Write-Host "Por favor, instala Python 3.10 o superior desde https://www.python.org/ y vuelve a ejecutar." -ForegroundColor Yellow
    exit 1
}

# 2. Configurar entorno virtual (venv)
$VenvDir = Join-Path $ScriptDir "venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvActivate = Join-Path $VenvDir "Scripts\Activate.ps1"

if (-not (Test-Path $VenvDir)) {
    Write-Host "[INFO] Creando entorno virtual Python en '$VenvDir'..." -ForegroundColor Cyan
    & $pythonCmd.Source -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Falló la creación del entorno virtual." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Entorno virtual creado exitosamente." -ForegroundColor Green
}

# 3. Comprobar e instalar dependencias
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"
if (Test-Path $RequirementsFile) {
    # Verificar si rich está instalado como chequeo rápido
    $checkRich = & $VenvPython -c "import rich, openai; from google import genai" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INFO] Instalando librerías requeridas (esto solo se realiza la primera vez)..." -ForegroundColor Cyan
        & $VenvPython -m pip install --upgrade pip --quiet
        & $VenvPython -m pip install -r $RequirementsFile --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[AVISO] Hubo advertencias al instalar dependencias. Intentando continuar..." -ForegroundColor Yellow
        } else {
            Write-Host "[OK] Dependencias instaladas correctamente." -ForegroundColor Green
        }
    }
}

# 4. Comprobar archivo .env
$EnvFile = Join-Path $ScriptDir ".env"
$EnvExample = Join-Path $ScriptDir ".env.example"

if (-not (Test-Path $EnvFile)) {
    if (Test-Path $EnvExample) {
        Copy-Item $EnvExample $EnvFile
        Write-Host "[AVISO] Se ha creado un archivo .env a partir de .env.example." -ForegroundColor Yellow
        Write-Host "Recuerda editar .env con tu API Key de Gemini, OpenAI o Claude." -ForegroundColor Yellow
    }
}

# 5. Ejecutar la aplicación principal
Write-Host "[INFO] Iniciando CTF-AI Solver..." -ForegroundColor Green
Write-Host ""

& $VenvPython "main.py" @ScriptArgs
