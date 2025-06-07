#!/usr/bin/env bash
# Script de construcción mejorado para Render

# Salir inmediatamente si algún comando falla
set -o errexit

# Imprimir cada comando antes de ejecutarlo
set -o xtrace

echo "Iniciando proceso de construcción..."

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --no-input

# Aplicar migraciones
echo "Aplicando migraciones a la base de datos..."
python manage.py migrate

echo "Proceso de construcción completado con éxito."
