@echo off
echo Iniciando servidor de comparacion de PDFs...
echo.
echo Configurando OPENAI_API_KEY...
set OPENAI_API_KEY=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

echo Iniciando servidor con uvicorn...
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause

