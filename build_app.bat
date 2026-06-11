@echo off
chcp 65001 > nul
echo ============================================
echo   Build - Contador de Agua
echo ============================================
echo.

:: Verifica Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale em python.org
    pause
    exit /b 1
)

:: Instala dependencias
echo [1/3] Instalando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

pip install pyinstaller --quiet

:: Aviso sobre icone
if not exist "assets\icon.ico" (
    echo.
    echo [AVISO] assets\icon.ico nao encontrado.
    echo         O .exe sera gerado sem icone personalizado.
    echo         Coloque o arquivo icon.ico em assets\ e rode novamente.
    echo.
    :: Gera o exe sem icone editando spec temporariamente
    python -c "
content = open('ContadorAgua.spec', encoding='utf-8').read()
content = content.replace(\"icon='assets\\\\icon.ico'\", 'icon=None')
open('ContadorAgua_tmp.spec', 'w', encoding='utf-8').write(content)
"
    set SPEC_FILE=ContadorAgua_tmp.spec
) else (
    set SPEC_FILE=ContadorAgua.spec
)

:: Build
echo [2/3] Gerando ContadorAgua.exe...
pyinstaller %SPEC_FILE% --noconfirm --clean
if errorlevel 1 (
    echo [ERRO] Build falhou.
    if exist ContadorAgua_tmp.spec del ContadorAgua_tmp.spec
    pause
    exit /b 1
)

if exist ContadorAgua_tmp.spec del ContadorAgua_tmp.spec

:: Resultado
echo [3/3] Concluido!
echo.
echo  Arquivo gerado: dist\ContadorAgua.exe
echo  Tamanho:
for %%f in (dist\ContadorAgua.exe) do echo    %%~zf bytes
echo.
echo  Basta enviar o ContadorAgua.exe para qualquer pessoa.
echo  Nao precisa de Python instalado para rodar.
echo.
pause
