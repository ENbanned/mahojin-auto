import platform
from typing import Dict

from curl_cffi.requests import BrowserType


DEFAULT_HEADERS: Dict[str, str] = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
}

if platform.system() == "Windows":
    DEFAULT_BROWSER = BrowserType.chrome124
else:
    DEFAULT_BROWSER = BrowserType.chrome131

DEFAULT_TIMEOUT: float = 60.0
DEFAULT_DISABLE_SSL: bool = True
