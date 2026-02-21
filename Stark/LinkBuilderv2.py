# Library import
import argparse
import pathlib
import sys
from constructor import LinkConstructor
import logging
import time

# Parameters configuration
def setup_custom_logger(name: str):
    """Configura el logger global para el ecosistema Stark."""
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Handler para archivo (Auditoría)
    file_handler = logging.FileHandler('linkbuilder_build.log')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def configure_arguments():
    argparser = argparse.ArgumentParser(
        description="LinkBuilder: Constructor inteligente de software modular Stark.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 1. Definición de Objetivos
    target_group = argparser.add_argument_group('Target Specifications')
    target_group.add_argument("--os", choices=["WINDOWS", "GNU/LINUX", "MACOS"], required=True)
    target_group.add_argument("--arch", choices=["X64", "X32", "ARM"], required=True)

    # 2. Rutas de Construcción
    path_group = argparser.add_argument_group('Build Paths')
    path_group.add_argument("--source", type=str, default="application/link")
    path_group.add_argument("--output", type=str, required=True)

    # 3. Modos de Operación
    mode_group = argparser.add_argument_group('Build Modes')
    mode_group.add_argument("--interactive", action="store_true")

    return argparser.parse_args()

if __name__ == "__main__":
    # Configure logger
    logger = setup_custom_logger("LinkBuilder")
    args = configure_arguments()
    
    source_path = pathlib.Path(args.source)
    if not source_path.exists():
        print(f"[!] Error: La ruta de origen '{args.source}' no existe.")
        logger.error(f"The source path: {args.source}, not exists")
        sys.exit(1)

    print(f"[*] Iniciando LinkBuilder para {args.os} ({args.arch})...")
    logger.info(f"Starting system for platform: {args.os}, and architecture: {args.arch}")

    # Instanciación del core
    constructor = LinkConstructor(
        platform_objective=args.os,
        architecture_objective=args.arch,
        application_rootpath=args.source
    )
    
    # Inicio del proceso de construcción
    if constructor.build():
        print("[+] Proceso de construcción finalizado exitosamente.")

    logger.info("Finishing system")
    sys.exit(0)