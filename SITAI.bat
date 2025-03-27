@echo off
echo Iniciando SITAI - Sistema de Catalogacao de Escavacoes Arqueologicas
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando aplicacao...
python -m streamlit run app.py
pause
