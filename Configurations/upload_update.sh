#!/bin/bash

# Configuracion
PACKAGE_NAME="configurations-stc";
PYPROJECT_FILE="pyproject.toml";

echo "[*] Iniciando proceso de actualizacion...";

# 1. Limpieza
rm -rf dist/ build/ *.egg-info;
find . -type d -name "__pycache__" -exec rm -rf {} +;

# 2. Incremento de version
if [ -f "$PYPROJECT_FILE" ]; then
    CURRENT_VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' "$PYPROJECT_FILE")
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{$NF = $NF + 1;} OFS="." {print $1, $2, $3}')
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    echo "[+] Nueva versión establecida: $NEW_VERSION"
else
    echo "[!] Error: No se encontró el archivo $PYPROJECT_FILE"; exit 1
fi

# 3. Compilacion y PyPI
python3 -m build
python3 -m twine upload dist/*

# 4. Sincronización GitHub
echo -n "[?] ¿Deseas actualizar el repositorio en Github? (Y/n): ";
read -r response;

case "$response" in
    [yY][eE][sS]|[yY]|"")
        if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
            git add .
            git commit -m "Configurations-STC: Automated update v$NEW_VERSION"
            git push origin main
            
            # --- NUEVA LÓGICA DE TAGS ---
            echo -n "[?] ¿Es esta una versión oficial (Release)? Esto añadirá un Tag en Github. (y/N): ";
            read -r tag_response;
            
            if [[ "$tag_response" =~ ^[yY]$ ]]; then
                TAG_NAME="configurations-stc-v$NEW_VERSION"
                echo "[*] Creando etiqueta de versión: $TAG_NAME..."
                git tag -a "$TAG_NAME" -m "Release oficial de $PACKAGE_NAME versión $NEW_VERSION"
                git push origin "$TAG_NAME"
                echo "[+] Tag publicado correctamente."
            else
                echo "[*] Actualización cotidiana finalizada sin etiquetas."
            fi
            # ----------------------------
        else
            echo "[!] Error: No se detectó repositorio Git.";
        fi
        ;;
    *) echo "[*] Omitiendo GitHub."; ;;
esac

echo "[*] Finalizando actualizacion del sistema.";