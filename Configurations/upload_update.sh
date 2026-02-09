#!/bin/bash

# Configuracion
PACKAGE_NAME="configurations-stc";
PYPROJECT_FILE="pyproject.toml";

echo "[*] Iniciando proceso de actualizacion...";

# Eliminacion de residuos de compilaciones previas
echo "[*] Eliminando residuos de compilaciones previas...";
rm -rf dist/ build/ *.egg-info;

echo "[*] Eliminando residuos de ejecuciones previas...";
find . -type d -name "__pycache__" -exec rm -rf {} +;

# Deteccion e incremento de version
if [ -f "$PYPROJECT_FILE" ]; then
    CURRENT_VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' "$PYPROJECT_FILE")
    echo "[+] Version actual: $CURRENT_VERSION";

    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{$NF = $NF + 1;} OFS="." {print $1, $2, $3}')
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    echo "[+] Nueva versión establecida: $NEW_VERSION"
else
    echo "[!] Error: No se encontró el archivo $PYPROJECT_FILE"; exit 1
fi

# Compilacion del nuevo paquete
echo "[*] Compilando recursos del nuevo paquete...";
python3 -m build

# Publicacion del nuevo paquete
echo "[*] Publicando nuevo paquete en PyPi...";
if python3 -m twine upload dist/*; then
    echo "[+] Publicación en PyPI exitosa."
else
    echo "[!] Error crítico en la publicacion a PyPI. Abortando proceso"
    exit 1
fi

# Sincronización con GitHub
echo -n "[?] ¿Deseas actualizar el repositorio en Github? (y/N): ";
read -r response;

case "$response" in
    [yY][eE][sS]|[yY]|"")
        if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
            git add .
            git commit -m "Configurations-STC: Actualizacion automatica v$NEW_VERSION"
            git push origin main
            
            # Configuracion de etiquetas (tags) de Github
            echo -n "[?] ¿Es esta una versión oficial? (Esto añadirá un Tag en Github). (y/N): ";
            read -r tag_response;
            
            if [[ "$tag_response" =~ ^[yY]$ ]]; then
                TAG_NAME="configurations-stc-v$NEW_VERSION"
                echo "[*] Creando etiqueta de versión: $TAG_NAME..."
                git tag -a "$TAG_NAME" -m "Release oficial de $PACKAGE_NAME versión $NEW_VERSION"
                git push origin "$TAG_NAME"
                echo "[+] Etiqueta publicada correctamente."
            else
                echo "[*] Actualización finalizada sin etiquetas."
            fi
            # ----------------------------
        else
            echo "[!] Error: No se detectó repositorio Git.";
        fi
        ;;
    *) echo "[*] Omitiendo sincronizacion con GitHub."; ;;
esac

echo "[*] Finalizando actualizacion del sistema.";