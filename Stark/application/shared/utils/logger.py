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

# Classes definition
class LocalFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

# Functions definition
def logger(name: str):
    log = logging.getLogger(name)

    if not log.handlers:
        log.setLevel(_determine_log_level())
        log.propagate = False


        handler = LocalFileHandler(
            "S-LINK.log",
            mode="a",
            encoding="UTF-8"
        )

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        handler.setFormatter(formatter)

        log.addHandler(handler)

    return log