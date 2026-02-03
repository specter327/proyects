#!/bin/bash

# Configuracion
PACKAGE_NAME="configurations-stc";
PYPROJECT_FILE="pyproject.toml";

echo "[*] Iniciando proceso de actualizacion...";

# 1. Limpieza residual
echo "[*] Eliminando carpetas residuales de compilaciones y ejecuciones...";
rm -rf dist/ build/ *.egg-info;
find . -type d -name "__pycache__" -exec rm -rf {} +;

# 2. Actualizacion de version
if [ -f "$PYPROJECT_FILE" ]; then
    CURRENT_VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' "$PYPROJECT_FILE")
    echo "[+] Versión actual: $CURRENT_VERSION"
    
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{$NF = $NF + 1;} OFS="." {print $1, $2, $3}')
    
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    echo "[+] Nueva versión establecida: $NEW_VERSION"
else
    echo "[!] Error: No se encontró el archivo $PYPROJECT_FILE"
    exit 1
fi

# 3. Compilacion y PyPI
echo "[*] Compilando nueva version del paquete...";
python3 -m build

echo "[*] Publicando en PyPi...";
python3 -m twine upload dist/*

# 4. Sincronización GitHub (Ajustada para Monorepos)
echo -n "[?] ¿Deseas actualizar el repositorio en Github? (Y/n): ";
read -r response;

case "$response" in
    [yY][eE][sS]|[yY]|"")
        echo "[*] Iniciando sincronizacion con Github...";
        
        # Verificamos si estamos dentro de un work tree de Git (aunque sea un monorepo)
        if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
            git add .
            git commit -m "Configurations-STC: Automated update v$NEW_VERSION"
            git push origin main
            echo "[+] Sincronizacion completada.";
        else
            echo "[!] Error: No se detecto un repositorio Git en la jerarquía de: $(pwd)";
        fi
        ;;
    [nN]*)
        echo "[*] Omitiendo sincronizacion con Github";
        ;;
    *)
        echo "[!] Respuesta no reconocida. Omitiendo GitHub.";
        ;;
esac

echo "[*] Finalizando actualizacion del sistema.";