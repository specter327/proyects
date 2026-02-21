# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
import logging
import time
import sys

# Constants definition
LOG_LEVELS = {
    "--quiet": logging.ERROR,    # Solo errores críticos
    "--info": logging.INFO,      # Flujo normal de ejecución (Por defecto)
    "--debug": logging.DEBUG,    # Información detallada (Decoradores, variables)
    "--trace": logging.NOTSET    # Nivel más bajo (Futuro uso)
}

def _determine_log_level() -> int:
    """
    Escanea sys.argv para determinar el nivel global de logging.
    Retorna logging.INFO por defecto si no se especifica.
    """
    for arg in sys.argv:
        if arg in LOG_LEVELS:
            return LOG_LEVELS[arg]
    return logging.INFO

# Functions definition
def logger(name: str) -> logging.Logger:
    logger_obj = logging.getLogger(name)
    
    # 1. Definimos el nombre del archivo de forma estática la primera vez
    if not hasattr(logger, "_shared_filename"):
        t = time.localtime()
        logger._shared_filename = f"Stark-Link [{t.tm_mday}-{t.tm_mon}-{t.tm_year}:{t.tm_hour}:{t.tm_min}:{t.tm_sec}].log"

        # Determine the log level with the software parameters (sys.argv)
        logger._global_level = _determine_log_level()

    if not logger_obj.handlers:
        logger_obj.setLevel(logger._global_level)
        
        # 2. Todos los módulos usan el mismo nombre almacenado en la función
        handler = logging.FileHandler(logger._shared_filename, encoding="UTF-8")
        formatter = logging.Formatter('%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s')
        handler.setFormatter(formatter)
        
        logger_obj.addHandler(handler)
        logger_obj.propagate = False
        
    return logger_obj