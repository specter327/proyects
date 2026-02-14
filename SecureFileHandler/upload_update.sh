#!/bin/bash

# Configuración específica del proyecto
PACKAGE_NAME="securefilehandler";
INTERNAL_NAME="securefilehandler";
PYPROJECT_FILE="pyproject.toml";

echo "[*] Iniciando proceso de actualización para $PACKAGE_NAME...";

# 1. Limpieza de entorno
echo "[*] Eliminando residuos de compilaciones previas...";
rm -rf dist/ build/ *.egg-info;

echo "[*] Eliminando residuos de ejecución (__pycache__)...";
find . -type d -name "__pycache__" -exec rm -rf {} +;

# 2. Gestión de versión en pyproject.toml
if [ -f "$PYPROJECT_FILE" ]; then
    CURRENT_VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' "$PYPROJECT_FILE")
    echo "[+] Versión detectada: $CURRENT_VERSION"
    
    # Incremento semántico simple (Z -> Z+1)
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{$NF = $NF + 1;} OFS="." {print $1, $2, $3}')
    
    # Aplicar cambio en el archivo
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    echo "[+] Nueva versión establecida: $NEW_VERSION"
else
    echo "[!] Error crítico: No se encontró $PYPROJECT_FILE"
    exit 1
fi

# 3. Compilación (Build)
# Requiere: python3 -m pip install build
echo "[*] Compilando distribución wheel y sdist...";
if python3 -m build; then
    echo "[+] Compilación exitosa."
else
    echo "[!] Error en la compilación. Verifique dependencias."
    exit 1
fi

# 4. Publicación en PyPI
# Requiere: python3 -m pip install twine
echo "[*] Publicando en PyPI...";
if python3 -m twine upload dist/* --verbose; then
    echo "[+] Publicación en PyPI completada."
else
    echo "[!] Error en la carga a PyPI. Abortando proceso."
    exit 1
fi

# 5. Sincronización con GitHub (Monorepo)
echo -n "[?] ¿Deseas actualizar el repositorio en GitHub? (Y/n): ";
read -r response;

case "$response" in
    [yY][eE][sS]|[yY]|"")
        echo "[*] Sincronizando con el repositorio remoto...";
        
        if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
            git add .
            git commit -m "$INTERNAL_NAME: auto-update v$NEW_VERSION";
            git push origin main;
            
            # 6. Etiquetado (Tagging) para Releases
            echo -n "[?] ¿Crear etiqueta de versión oficial (Tag)? (y/N): ";
            read -r tag_response;

            if [[ "$tag_response" =~ ^[yY]$ ]]; then
                TAG_NAME="$INTERNAL_NAME-v$NEW_VERSION"
                echo "[*] Generando tag: $TAG_NAME..."
                git tag -a "$TAG_NAME" -m "Release $INTERNAL_NAME versión $NEW_VERSION"
                git push origin "$TAG_NAME"
                echo "[+] Tag publicado en GitHub."
            else
                echo "[*] Proceso finalizado sin etiquetas."
            fi
        else
            echo "[!] Advertencia: No se detectó un entorno Git activo."
        fi
        ;;
    [nN]*)
        echo "[*] Sincronización omitida."
        ;;
esac

echo "[*] Actualización de $PACKAGE_NAME finalizada con éxito.";