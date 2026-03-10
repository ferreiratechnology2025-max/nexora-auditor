@echo off
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
for %%I in ("%ROOT%.") do set "ROOT=%%~fI"
cd /d "%ROOT%"

title Nexora Agente - Boot Unificado

echo [BOOT] Resolvendo interpretador Python...
set "PYTHON_EXE=%ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado. Ajuste PYTHON_EXE no start_nexora.bat.
  exit /b 1
)

echo [BOOT] Verificando Docker daemon...
docker info >nul 2>&1
if errorlevel 1 (
  if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
    echo [BOOT] Iniciando Docker Desktop...
    start "Docker Desktop" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 12 >nul
  ) else (
    echo [AVISO] Docker Desktop nao encontrado no caminho padrao.
  )
)

docker info >nul 2>&1
if errorlevel 1 (
  echo [AVISO] Docker daemon indisponivel. O app sera iniciado mesmo assim.
) else (
  docker ps -a --format "{{.Names}}" | findstr /i /x "nexora_sandbox" >nul
  if not errorlevel 1 (
    echo [BOOT] Iniciando container persistente nexora_sandbox...
    docker start nexora_sandbox >nul 2>&1
  )
)

echo [BOOT] Indexando genes...
%PYTHON_EXE% scripts\update_genome.py

echo [BOOT] Iniciando Streamlit...
start "Nexora Dashboard" %PYTHON_EXE% -m streamlit run app.py --server.port 8501 --server.headless false

timeout /t 2 >nul
start "" http://localhost:8501

echo [OK] Nexora inicializado em http://localhost:8501
exit /b 0
