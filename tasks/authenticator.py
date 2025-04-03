import time
import logging
from typing import Dict, Optional
from urllib.parse import urlencode

from eth_account.messages import encode_defunct

from tls_client.client import TLSClient

logger = logging.getLogger(__name__)


class Authenticator:
    def __init__(self, tls_client: TLSClient):
        self.client = tls_client
        self.jwt_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.wallet_address: Optional[str] = None
        self.auth_cookies: Dict[str, str] = {}
    
    
    async def get_nonce(self) -> str:
        logger.info("Получение nonce для аутентификации")
        
        url = "https://app.dynamicauth.com/api/v0/sdk/f710531c-6197-4279-b201-cfde7e6195e4/nonce"
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/",
            "x-dyn-api-version": "API/0.0.570",
            "x-dyn-version": "WalletKit/3.9.5"
        }
        
        response = await self.client.get(url, headers=headers)
        data = response.json()
        
        if "nonce" not in data:
            raise ValueError(f"Не удалось получить nonce: {data}")
        
        logger.debug(f"Получен nonce: {data['nonce']}")
        return data["nonce"]
    
    
    def prepare_sign_message(self, wallet_address: str, nonce: Optional[str] = None) -> str:
        """Подготавливает сообщение для подписи"""
        if nonce is None:
            nonce = hex(int(time.time() * 1000))[2:]
        
        message = (
            f"app.mahojin.ai wants you to sign in with your Ethereum account:\n"
            f"{wallet_address}\n\n"
            f"Welcome to Hypetech.Ltd. Signing is the only way we can truly know that you are the owner of the wallet you are connecting. "
            f"Signing is a safe, gas-less transaction that does not in any way give Hypetech.Ltd permission to perform any transactions with your wallet.\n\n"
            f"URI: https://app.mahojin.ai/images\n"
            f"Version: 1\n"
            f"Chain ID: 1514\n"
            f"Nonce: {nonce}\n"
            f"Issued At: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())}\n"
            f"Request ID: f710531c-6197-4279-b201-cfde7e6195e4"
        )
        
        return message
    
    
    def sign_message(self, evm_client, message: str) -> str:
        logger.info("Подписание сообщения для аутентификации")
        
        encoded_message = encode_defunct(text=message)
        signed = evm_client.web3.eth.account.sign_message(encoded_message, private_key=evm_client.private_key)
        
        logger.debug(f"Сообщение подписано: {signed.signature.hex()}")
        return signed.signature.hex()
    
    
    async def authenticate(self, evm_client) -> bool:
        self.wallet_address = evm_client.account.address
        
        nonce = await self.get_nonce()
        message = self.prepare_sign_message(self.wallet_address, nonce)
        signature = self.sign_message(evm_client, message)
        
        verify_url = "https://app.dynamicauth.com/api/v0/sdk/f710531c-6197-4279-b201-cfde7e6195e4/verify"
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/",
            "x-dyn-api-version": "API/0.0.570",
            "x-dyn-version": "WalletKit/3.9.5"
        }
        
        payload = {
            "signedMessage": signature,
            "messageToSign": message,
            "publicWalletAddress": self.wallet_address,
            "chain": "EVM",
            "walletName": "metamask",
            "walletProvider": "browserExtension",
            "network": "1514",
            "additionalWalletAddresses": []
        }
        
        response = await self.client.post(verify_url, json=payload, headers=headers)
        auth_data = response.json()
        
        if "jwt" not in auth_data:
            logger.error(f"Ошибка аутентификации: {auth_data}")
            return False
        
        self.jwt_token = auth_data["jwt"]
        self.user_id = auth_data["user"]["id"]
        
        logger.info(f"Успешная аутентификация. User ID: {self.user_id}")
        
        session_url = "https://app.mahojin.ai/api/auth/session"
        session_headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/"
        }
        
        data = await self.client.get(session_url, headers=session_headers)
                
        csrf_url = "https://app.mahojin.ai/api/auth/csrf"
        csrf_response = await self.client.get(csrf_url, headers=session_headers)
        
        csrf_data = csrf_response.json()
        if "csrfToken" not in csrf_data:
            logger.error(f"Ошибка получения CSRF-токена: {csrf_data}")
            return False
        
        csrf_token = csrf_data["csrfToken"]
        
        dynamic_labs_req_url = "https://app.mahojin.ai/api/auth/callback/dynamic_labs"
        dynamic_data = {
            'token': self.jwt_token,
            'referralId': '',
            'redirect': 'false',
            'csrfToken': csrf_token,
            'callbackUrl': 'https://app.mahojin.ai/images?sortBy=featured&creationFilter=all',
            'json': 'true',
        }
        
        encoded_data = urlencode(dynamic_data)

        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/"
        }

        dynamic_labs_req_url_response = await self.client.post(
            url=dynamic_labs_req_url, 
            headers=headers, 
            data=encoded_data
        ) 
        
        
        check_session = await self.client.get(session_url, headers=session_headers)
        session_data = check_session.json()
        
        if "user" in session_data and session_data["user"].get("wallet_address") == self.wallet_address:
            logger.info("Сессия успешно получена")
            self.auth_cookies = dict(self.client.cookies)
            return True
        else:
            logger.error(f"Ошибка получения сессии: {session_data}")
            return False
        