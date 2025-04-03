import inspect
import logging
import random
import time
import asyncio
import warnings
from typing import Any, Dict, Optional, TypeVar

from curl_cffi.requests import AsyncSession, Response

from .config import (
    DEFAULT_BROWSER, 
    DEFAULT_DISABLE_SSL, 
    DEFAULT_HEADERS, 
    DEFAULT_TIMEOUT
)
from .decorators import log_request
from .exceptions import TLSClientError
from .types import HeadersType, ProxyType
from .fingerprint_randomizer import FingerprintRandomizer


T = TypeVar('T')
warnings.filterwarnings("ignore", module="curl_cffi")


class TLSClient:
    def __init__(
        self,
        proxy: ProxyType = None,
        headers: Optional[HeadersType] = None,
        browser_type: Any = None,
        timeout: float = DEFAULT_TIMEOUT,
        disable_ssl: bool = DEFAULT_DISABLE_SSL,
        randomize_fingerprint: bool = True
    ) -> None:
        self._proxy = proxy
        self._timeout = timeout
        self._randomize_fingerprint = randomize_fingerprint
        self._session_lock = asyncio.Lock()
        self._is_closed = False
        self._browser_type = browser_type
        self._disable_ssl = disable_ssl
        self._headers = headers or {}
        
        if randomize_fingerprint:
            random_headers, random_browser_type = FingerprintRandomizer.get_random_fingerprint()
            self._init_headers = dict(random_headers)
            self._browser_type = self._browser_type or random_browser_type
        else:
            self._init_headers = dict(DEFAULT_HEADERS)
            self._browser_type = self._browser_type or DEFAULT_BROWSER
            
        if headers:
            self._init_headers.update(headers)

        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Инициализация TLS клиента с User-Agent: {self._init_headers.get('User-Agent', 'не указан')}")

        self._session = AsyncSession(
            impersonate=self._browser_type,
            headers=self._init_headers,
            proxies={"http": proxy, "https": proxy} if proxy else {},
            verify=not disable_ssl,
        )
       
        
    async def _recreate_session(self) -> None:
        async with self._session_lock:
            if self._is_closed:
                return
                
            if self._session:
                try:
                    if inspect.iscoroutinefunction(self._session.close):
                        await self._session.close()
                    else:
                        self._session.close()
                except Exception as e:
                    self.logger.debug(f"Ошибка при закрытии старой сессии: {str(e)}")
                
                await asyncio.sleep(0.2)
            
            try:
                if self._randomize_fingerprint:
                    random_headers, random_browser_type = FingerprintRandomizer.get_random_fingerprint()
                    init_headers = dict(random_headers)
                    browser_type = self._browser_type or random_browser_type
                else:
                    init_headers = dict(DEFAULT_HEADERS)
                    browser_type = self._browser_type
                    
                if self._headers:
                    init_headers.update(self._headers)
                
                self._session = AsyncSession(
                    impersonate=browser_type,
                    headers=init_headers,
                    proxies={"http": self._proxy, "https": self._proxy} if self._proxy else {},
                    verify=not self._disable_ssl,
                )
                
                self.logger.debug("Сессия успешно пересоздана")
            except Exception as e:
                self.logger.error(f"Ошибка при пересоздании сессии: {str(e)}")
                self._session = AsyncSession(
                    impersonate=DEFAULT_BROWSER,
                    headers=DEFAULT_HEADERS,
                    verify=not DEFAULT_DISABLE_SSL,
                )
        
        
    async def refresh_fingerprint(self) -> None:
        if self._is_closed:
            return
            
        if not self._randomize_fingerprint:
            self.logger.debug("Обновление отпечатка пропущено, так как рандомизация отключена")
            return
        
        await self._recreate_session()


    async def __aenter__(self) -> 'TLSClient':
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


    async def close(self) -> None:
        async with self._session_lock:
            if self._is_closed:
                return
                
            self._is_closed = True
            
            if self._session:
                try:
                    if inspect.iscoroutinefunction(self._session.close):
                        await self._session.close()
                    else:
                        self._session.close()
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии сессии: {str(e)}")
                finally:
                    self._session = None


    def update_headers(self, new_headers: Dict[str, str]) -> None:
        if self._is_closed or not self._session:
            return
            
        self._headers.update(new_headers)
        self._session.headers.update(new_headers)


    @property
    def cookies(self) -> Any:
        if self._is_closed or not self._session:
            return {}
        return self._session.cookies


    @log_request()
    async def request(self, method: str, url: str, *, headers: Optional[Dict[str, str]] = None, 
                    max_retries: int = 3, retry_delay: float = 1.0, **kwargs: Any) -> Response:
        if self._is_closed:
            raise TLSClientError("Клиент закрыт и не может выполнять запросы")
            
        original_timeout = kwargs.get("timeout", self._timeout)
        
        last_attempt_timeout = original_timeout * 1.5
        
        for attempt in range(max_retries):
            if "timeout" not in kwargs:
                if attempt == max_retries - 1:
                    kwargs["timeout"] = last_attempt_timeout
                else:
                    kwargs["timeout"] = original_timeout
                
            if headers:
                request_headers = dict(self._session.headers)
                request_headers.update(headers)
                kwargs["headers"] = request_headers

            try:
                method_lower = method.lower()
                request_task = None
                
                try:
                    if method_lower == "get":
                        request_task = asyncio.create_task(self._session.get(url, **kwargs))
                    elif method_lower == "post":
                        request_task = asyncio.create_task(self._session.post(url, **kwargs))
                    elif method_lower == "put":
                        request_task = asyncio.create_task(self._session.put(url, **kwargs))
                    elif method_lower == "delete":
                        request_task = asyncio.create_task(self._session.delete(url, **kwargs))
                    else:
                        raise TLSClientError(f"Unsupported method: {method}")
                    
                    current_timeout = kwargs.get("timeout", self._timeout)
                    resp = await asyncio.wait_for(request_task, timeout=current_timeout + 5.0)
                    return resp
                    
                except asyncio.TimeoutError:
                    if request_task and not request_task.done():
                        request_task.cancel()
                        try:
                            await request_task
                        except (asyncio.CancelledError, Exception):
                            pass
                    
                    self.logger.warning(f"Таймаут запроса (попытка {attempt+1}/{max_retries}): {url}")
                    
                    await self._recreate_session()
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при выполнении запроса (попытка {attempt+1}/{max_retries}): {str(e)}")
                    
                    await self._recreate_session()
                    raise
                
            except Exception as e:
                if isinstance(e, TLSClientError) and attempt == max_retries - 1:
                    raise
                
                self.logger.warning(f"Ошибка запроса (попытка {attempt+1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    backoff = retry_delay * (2 ** attempt) * (0.75 + 0.5 * random.random())
                    await asyncio.sleep(backoff)
                    continue
                else:
                    if not isinstance(e, TLSClientError):
                        raise TLSClientError(f"Request error after {max_retries} attempts: {str(e)}") from e
                    raise
        
        raise TLSClientError(f"Request failed for unknown reason after {max_retries} attempts")


    async def get(self, url: str, **kwargs: Any) -> Response:
        return await self.request("GET", url, **kwargs)


    async def post(self, url: str, **kwargs: Any) -> Response:
        return await self.request("POST", url, **kwargs)


    async def put(self, url: str, **kwargs: Any) -> Response:
        return await self.request("PUT", url, **kwargs)


    async def delete(self, url: str, **kwargs: Any) -> Response:
        return await self.request("DELETE", url, **kwargs)
    