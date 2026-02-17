# Library import
import logging
import time

# Functions definition
def logger(name: str, debug_mode: bool = False) -> logging.Logger:
    logger_obj = logging.getLogger(name)
    
    # 1. Definimos el nombre del archivo de forma estática la primera vez
    if not hasattr(logger, "_shared_filename"):
        t = time.localtime()
        logger._shared_filename = f"Stark-Link [{t.tm_mday}-{t.tm_mon}-{t.tm_year}:{t.tm_hour}:{t.tm_min}:{t.tm_sec}].log"

    if not logger_obj.handlers:
        logger_obj.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        # 2. Todos los módulos usan el mismo nombre almacenado en la función
        handler = logging.FileHandler(logger._shared_filename, encoding="UTF-8")
        formatter = logging.Formatter('%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s')
        handler.setFormatter(formatter)
        
        logger_obj.addHandler(handler)
        logger_obj.propagate = False
        
    return logger_obj