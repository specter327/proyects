# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
import functools
import time
import logging
from typing import Callable, Any
from .logger import logger

# Functions definition
def smart_debug(element_name: str, include_args: bool = True, include_result: bool = True):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_handler = logger(element_name)
            start_time = time.perf_counter()
            
            # Logging de entrada
            if include_args:
                log_handler.debug(f"EXEC: {func.__name__} | ARGS: {args} | KWARGS: {kwargs}")
            else:
                log_handler.debug(f"EXEC: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                
                # Cálculo de latencia
                end_time = time.perf_counter()
                latency = end_time - start_time

                # Logging de salida
                if include_result:
                    log_handler.debug(f"END: {func.__name__} | RESULT: {result} | TIME: {latency:.4f}s")
                else:
                    log_handler.debug(f"END: {func.__name__} | TIME: {latency:.4f}s")
                
                return result

            except Exception as e:
                log_handler.error(f"FAIL: {func.__name__} | ERROR: {str(e)}", exc_info=True)
                raise e
        return wrapper
    return decorator