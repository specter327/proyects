#!/bin/bash

BASE_DIR="/home/specter/Escritorio/proyects/Stark"
DIST_DIR="$BASE_DIR/distribution_link"
HOOKS_DIR="$DIST_DIR/hooks"

echo "[*] Iniciando Pipeline de Compilación Técnica..."

# 1. Limpieza y preparación
rm -rf "$DIST_DIR/build" "$DIST_DIR/dist" "$DIST_DIR/*.spec" "$HOOKS_DIR"
mkdir -p "$HOOKS_DIR"
rm -rf ~/.cache/pyinstaller

# 2. Sincronizar distribución
python3 "$BASE_DIR/LinkBuilder.py"
cd "$DIST_DIR" || exit
export PYTHONPATH=$(pwd)

# 3. CREACIÓN DE HOOK DE SOBRECARGA (El "Anti-Olvido")
# Este archivo fuerza a PyInstaller a seguir las dependencias de tus capas
cat <<EOF > "$HOOKS_DIR/hook-shared.py"
from PyInstaller.utils.hooks import collect_submodules, collect_all
hiddenimports = collect_submodules('shared') + collect_submodules('system') + [
    'uuid', 
    'datapackage', 
    'json', 
    'importlib',
    'cryptography'
]
datas, binaries, hiddenimports_extra = collect_all('datapackage')
hiddenimports += hiddenimports_extra
EOF

echo "[*] Generando especificación de compilación forzada..."

# 4. Ejecución de PyInstaller con Inyección de Hidden Imports Directa
# Forzamos los imports mediante el flag --hidden-import repetido para asegurar el grafo
pyinstaller --noconfirm --onefile --console \
    --name "Stark-Link-Release" \
    --paths "." \
    --hidden-import="uuid" \
    --hidden-import="datapackage" \
    --hidden-import="json" \
    --hidden-import="shared" \
    --hidden-import="system" \
    --hidden-import="shared.communication_architecture.layers.communication" \
    --hidden-import="shared.communication_architecture.layers.protection" \
    --hidden-import="shared.communication_architecture.layers.security" \
    --hidden-import="shared.communication_architecture.layers.transport" \
    --collect-all "datapackage" \
    --collect-all "shared" \
    --collect-all "system" \
    --copy-metadata "datapackage-messages" \
    --clean \
    "Stark-Link.py"