@echo off
cd /d "%~dp0"

echo ======================================================
echo              KARAOKE PRO - INICIANDO
echo ======================================================

:: 1. Encontra o Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERRO] Python nao encontrado!
        echo Instale o Python em python.org e marque "Add to PATH".
        pause
        exit /b
    ) else (
        set PY_CMD=py
    )
) else (
    set PY_CMD=python
)
echo [OK] Python encontrado.

:: 2. Cria o venv se nao existir
if not exist "venv\" (
    echo [INFO] Criando ambiente virtual...
    %PY_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar venv.
        pause
        exit /b
    )
    echo [OK] Ambiente virtual criado.
)

:: 3. Ativa o venv
call venv\Scripts\activate

:: 4. Instala dependencias somente se ainda nao instalou com sucesso
if not exist "venv\instalado.txt" (
    echo [INFO] Instalando dependencias pela primeira vez...
    echo [INFO] Isso pode demorar varios minutos, aguarde...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERRO] Falha na instalacao das dependencias.
        pause
        exit /b
    )
    echo OK > venv\instalado.txt
    echo [OK] Dependencias instaladas com sucesso!
)

:: 5. Inicia o programa
echo [INFO] Iniciando Karaoke Pro...
python ui.py

echo.
echo ======================================================
echo   Programa encerrado. Pressione qualquer tecla para fechar.
echo ======================================================
pause