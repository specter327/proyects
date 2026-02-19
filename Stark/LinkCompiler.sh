#!/bin/bash

# Stark-Link Automated Compiler Pipeline
# Orientado a entornos de ciberseguridad / despliegue modular

# Configuración de rutas relativas
ROOT_DIR=$(pwd)
BUILD_SOURCE_DIR="$ROOT_DIR/distribution_link"
ENTRY_POINT="Stark-Link.py"
OUTPUT_NAME="Stark-Link-Release"

# Colores para feedback técnico
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}[*] Iniciando Pipeline de Compilación...${NC}"

# 1. Regenerar recursos con LinkBuilder
if [ -f "./LinkBuilder.py" ]; then
    echo -e "[*] Sincronizando recursos dinámicos con LinkBuilder..."
    python3 ./LinkBuilder.py
else
    echo -e "${RED}[!] Error: No se encuentra LinkBuilder.py en la raíz.${NC}"
    exit 1
fi

# 2. Entrar al directorio de distribución
cd "$BUILD_SOURCE_DIR" || exit

# 3. Limpieza profunda
echo -e "[*] Limpiando residuos de compilaciones previas..."
rm -rf build dist *.spec

# 4. Definición de módulos críticos para inyección dinámica
# (Aseguramos que PyInstaller no los ignore por ser carga reflexiva)
HIDDEN_IMPORTS=(
    "shared.communication_architecture.layers.transport.modules.tcpip"
    "shared.communication_architecture.layers.protection.modules.http"
    "shared.communication_architecture.layers.protection.modules.transparent"
    "shared.communication_architecture.layers.security.modules.rsa"
    "system.core.modules.communication_service"
    "system.install.modules.deploy_timestomp_linux"
    "system.install.modules.persistence_crontab_linux"
    "system.virtual_filesystem.gnulinux"
)

# Construir cadena de parámetros
IMPORT_CMD=""
for mod in "${HIDDEN_IMPORTS[@]}"; do
    IMPORT_CMD="$IMPORT_CMD --hidden-import=$mod"
done

# 5. Compilación Principal
echo -e "${BLUE}[*] Ejecutando PyInstaller (Modo Inyección Total)...${NC}"

# --collect-all asegura que capture los .pyc que ya generó tu proceso
pyinstaller --noconfirm --onefile --console \
    --name "$OUTPUT_NAME" \
    --add-data "shared:shared" \
    --add-data "system:system" \
    $IMPORT_CMD \
    --collect-all "shared" \
    --collect-all "system" \
    --clean \
    "$ENTRY_POINT"

# 6. Verificación Final
if [ -f "dist/$OUTPUT_NAME" ]; then
    echo -e "${GREEN}[+] Binario generado exitosamente en: $BUILD_SOURCE_DIR/dist/$OUTPUT_NAME${NC}"
    du -sh "dist/$OUTPUT_NAME"
else
    echo -e "${RED}[!] Error crítico: El binario no fue generado.${NC}"
    exit 1
fi