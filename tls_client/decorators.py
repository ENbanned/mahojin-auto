import functools
import logging
from typing import Any, Callable, TypeVar, Awaitable

T = TypeVar('T')


def log_request(logger: logging.Logger = None):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(self, method: str, url: str, *args: Any, **kwargs: Any) -> T:
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(__name__)
                
            logger.debug(f"TLSClient => {method.upper()} {url}, kwargs={kwargs}")
            try:
                result = await func(self, method, url, *args, **kwargs)
                logger.debug(f"TLSClient <= {method.upper()} {url}, status={getattr(result, 'status_code', 'unknown')}")
                return result
            except Exception as e:
                logger.error(f"TLSClient !! {method.upper()} {url}, error={str(e)}")
                raise
        return wrapper
    return decorator
