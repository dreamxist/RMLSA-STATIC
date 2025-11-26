#!/bin/bash

# RMLSA-STATIC - Script de instalación y ejecución
# Compatible con macOS y Linux

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "   RMLSA-STATIC - Simulador de Redes Ópticas"
    echo "=============================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header

# Verificar Python
print_info "Verificando instalación de Python..."

PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON_CMD=$cmd
            print_success "Python $version encontrado ($cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python 3.10 o superior no encontrado."
    echo ""
    echo "Por favor, instala Python 3.10+ desde:"
    echo "  - macOS: brew install python3"
    echo "  - Linux: sudo apt install python3 (o equivalente)"
    echo "  - Descarga: https://www.python.org/downloads/"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    print_info "Creando entorno virtual..."
    $PYTHON_CMD -m venv venv
    print_success "Entorno virtual creado"
else
    print_info "Entorno virtual existente detectado"
fi

# Activar entorno virtual
print_info "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# Instalar dependencias
print_info "Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_success "Dependencias instaladas"

# Ejecutar simulador
echo ""
echo -e "${BLUE}=============================================="
echo "   Ejecutando Simulador RMLSA"
echo -e "==============================================${NC}"
echo ""

python simulator.py

# Mensaje final
echo ""
echo -e "${GREEN}=============================================="
echo "   Simulación completada exitosamente"
echo "==============================================${NC}"
echo ""
echo "Archivos generados:"
echo "  - resultado_comparativa.png (gráfico comparativo)"
echo "  - assignments_details.txt (reporte detallado)"
echo ""
