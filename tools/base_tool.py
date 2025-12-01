"""Base Tool with Validation, Retry, and Timeout"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from functools import wraps
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0

def with_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator for tools"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_error
        return wrapper
    return decorator

def with_timeout(seconds: int):
    """Timeout decorator (simple version using signal - Unix only)"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Operation timed out after {seconds}s")
            
            # Set timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            return result
        return wrapper
    return decorator

class BaseTool(ABC):
    """Base class for all tools"""
    
    name: str = "base_tool"
    description: str = "Base tool"
    
    def __init__(self):
        from config import get_config
        self.config = get_config()
    
    @abstractmethod
    def _execute(self, input_str: str) -> ToolResult:
        """Override this in subclass"""
        pass
    
    def run(self, input_str: str) -> str:
        """Execute tool with logging and timing"""
        start = time.time()
        logger.info(f"[{self.name}] Executing with input: {input_str[:100]}...")
        
        try:
            result = self._execute(input_str)
            result.execution_time = time.time() - start
            
            if result.success:
                logger.info(f"[{self.name}] Success in {result.execution_time:.2f}s")
                return str(result.data)
            else:
                logger.error(f"[{self.name}] Failed: {result.error}")
                return f"Error: {result.error}"
                
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"[{self.name}] Exception after {elapsed:.2f}s: {e}")
            return f"Error: {str(e)}"
    
    def validate_input(self, input_str: str) -> tuple[bool, str]:
        """Override for custom validation"""
        if not input_str or not input_str.strip():
            return False, "Empty input"
        return True, ""
