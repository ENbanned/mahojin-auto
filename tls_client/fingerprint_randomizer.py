import random
from typing import Dict, Optional, Tuple

from curl_cffi.requests import BrowserType


class FingerprintRandomizer:
    CHROME_VERSIONS = ["99.0.4844.51", "100.0.4896.75", "101.0.4951.41", "102.0.5005.61", 
                       "103.0.5060.53", "104.0.5112.79", "105.0.5195.52", "106.0.5249.61",
                       "107.0.5304.87", "108.0.5359.71", "109.0.5414.74", "110.0.5481.77",
                       "111.0.5563.64", "112.0.5615.138", "113.0.5672.93", "114.0.5735.90", 
                       "115.0.5790.170", "116.0.5845.110", "117.0.5938.88", "118.0.5993.70",
                       "119.0.6045.124", "120.0.6099.109", "121.0.6167.85", "122.0.6261.94",
                       "123.0.6312.58", "124.0.6367.62", "131.0.6498.75", "134.0.6513.20"]
    
    FIREFOX_VERSIONS = ["90.0", "91.0", "92.0", "93.0", "94.0", "95.0", "96.0", "97.0", 
                       "98.0", "99.0", "100.0", "101.0", "102.0", "103.0", "104.0", "105.0",
                       "106.0", "107.0", "108.0", "109.0", "110.0", "111.0", "112.0", "113.0"]
    
    LANGUAGES = [
        "en-US,en;q=0.9", 
        "en-GB,en;q=0.8,en-US;q=0.9", 
        "en-CA,en-US;q=0.9,en;q=0.8",
        "en-AU,en-GB;q=0.9,en;q=0.8",
        "en-NZ,en-GB;q=0.9,en;q=0.8",
        "en-ZA,en-GB;q=0.9,en;q=0.8",
        "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
    ]
    
    OS_PLATFORMS = [
        ("Windows", ["10.0", "11.0"]),
        ("Macintosh", ["Intel Mac OS X 10_15", "Intel Mac OS X 11_0", "Intel Mac OS X 12_0", "Intel Mac OS X 13_0"]),
        ("X11", ["Linux x86_64", "Ubuntu; Linux x86_64", "Fedora; Linux x86_64"])
    ]
    
    @classmethod
    def get_random_browser_type(cls) -> BrowserType:
        """Возвращает случайный тип браузера из доступных в curl_cffi."""
        browser_types = [
            BrowserType.chrome99, BrowserType.chrome100, BrowserType.chrome101, 
            BrowserType.chrome104, BrowserType.chrome107, BrowserType.chrome110, 
            BrowserType.chrome116, BrowserType.chrome120, BrowserType.chrome124
        ]
        return random.choice(browser_types)
    
    @classmethod
    def generate_chrome_user_agent(cls) -> str:
        """Генерирует случайный User-Agent для Chrome."""
        os_platform, os_versions = random.choice(cls.OS_PLATFORMS)
        os_version = random.choice(os_versions)
        chrome_version = random.choice(cls.CHROME_VERSIONS)
        
        if os_platform == "Windows":
            return f"Mozilla/5.0 (Windows NT {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
        elif os_platform == "Macintosh":
            return f"Mozilla/5.0 (Macintosh; {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
        else:  # X11
            return f"Mozilla/5.0 ({os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
    
    @classmethod
    def generate_firefox_user_agent(cls) -> str:
        """Генерирует случайный User-Agent для Firefox."""
        os_platform, os_versions = random.choice(cls.OS_PLATFORMS)
        os_version = random.choice(os_versions)
        firefox_version = random.choice(cls.FIREFOX_VERSIONS)
        
        if os_platform == "Windows":
            return f"Mozilla/5.0 (Windows NT {os_version}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}"
        elif os_platform == "Macintosh":
            return f"Mozilla/5.0 (Macintosh; {os_version}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}"
        else:  # X11
            return f"Mozilla/5.0 ({os_version}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}"
    
    @classmethod
    def generate_random_headers(cls) -> Dict[str, str]:
        """Генерирует случайные заголовки HTTP."""
        browser_choice = random.choice(["chrome", "firefox"])
        
        if browser_choice == "chrome":
            user_agent = cls.generate_chrome_user_agent()
        else:
            user_agent = cls.generate_firefox_user_agent()
        
        accept_language = random.choice(cls.LANGUAGES)
        
        headers = {
            "Accept": "*/*",
            "Accept-Language": accept_language,
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": random.choice(["keep-alive", "close"]),
            "Sec-Ch-Ua-Platform": f'"{random.choice(["Windows", "macOS", "Linux"])}"',
            "Sec-Ch-Ua-Mobile": random.choice(["?0", "?1"]),
            "Sec-Fetch-Dest": random.choice(["empty", "document"]),
            "Sec-Fetch-Mode": random.choice(["cors", "navigate"]),
            "Sec-Fetch-Site": random.choice(["same-origin", "same-site", "cross-site"]),
            "Dnt": random.choice(["0", "1"])
        }
        
        # Случайно удаляем некоторые заголовки для большей вариативности
        for header in list(headers.keys()):
            if random.random() < 0.2 and header not in ["User-Agent", "Accept"]:
                del headers[header]
                
        return headers
    
    @classmethod
    def get_random_fingerprint(cls) -> Tuple[Dict[str, str], BrowserType]:
        """Возвращает случайные заголовки и тип браузера."""
        headers = cls.generate_random_headers()
        browser_type = cls.get_random_browser_type()
        return headers, browser_type