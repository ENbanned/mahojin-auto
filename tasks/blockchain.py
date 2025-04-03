import json
import logging
import asyncio
from typing import Dict, Any, List

from web3 import Web3
from web3.exceptions import TransactionNotFound

from evm.client import EVMClient

logger = logging.getLogger(__name__)


class BlockchainManager:
    def __init__(self, evm_client: EVMClient):
        self.client = evm_client
        self.contract_address = "0xcC2E862bCee5B6036Db0de6E06Ae87e524a79fd8"
        self.abi_file = "license_attachment.json"
        self._abi = None
        self._contract = None
    
    
    @property
    def abi(self) -> List[Dict[str, Any]]:
        if self._abi is None:
            try:
                with open(f"evm/abis/{self.abi_file}", "r", encoding="utf-8") as f:
                    self._abi = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Ошибка при загрузке ABI: {e}")
                raise
        return self._abi
    
    
    @property
    def contract(self):
        if self._contract is None:
            self._contract = self.client.web3.eth.contract(
                address=self.contract_address,
                abi=self.abi
            )
        return self._contract
    
    
    async def mint_image_nft(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Начало процесса минтинга NFT")
        
        try:
            spg_nft_contract = Web3.to_checksum_address("0xb4D6411f44767a4C093CEFbf584cA9369849DB01")
            recipient = self.client.account.address
            
            ip_metadata = (
                metadata["metadata_url"],
                Web3.keccak(text=metadata["metadataHash"]),
                metadata["metadata_url"],
                Web3.keccak(text=metadata["metadataHash"])
            )
            
            license_terms = [(
                (
                    True,
                    "0x9156e603C949481883B1d3355c6f1132D191fC41",
                    0,
                    0,
                    True,
                    True,
                    "0x0000000000000000000000000000000000000000",
                    b"",
                    10000000, 
                    0, 
                    True,  
                    True, 
                    False,  
                    True, 
                    0,  
                    "0x1514000000000000000000000000000000000000",
                    ""  
                ),
                (  
                    False,  
                    0,  
                    "0x0000000000000000000000000000000000000000",  
                    b"",  
                    0,  
                    False,  
                    0,  
                    "0x0000000000000000000000000000000000000000"
                )
            )]
            
            allow_duplicates = False
            
            function_data = self.contract.encodeABI(
                fn_name='mintAndRegisterIpAndAttachPILTerms',
                args=[
                    spg_nft_contract,
                    recipient,
                    ip_metadata,
                    license_terms,
                    allow_duplicates
                ]
            )
            
            tx = await self.client.build_transaction(
                to=self.contract_address,
                data=function_data
            )
            
            tx_hash = await self.client.send_transaction(tx)
            logger.info(f"Транзакция отправлена, хеш: {tx_hash}")
            
            tx_receipt = await self._wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt["status"] == 1:
                logger.info(f"Транзакция успешно выполнена! Блок: {tx_receipt['blockNumber']}")
                
                return {
                    "success": True,
                    "transaction_hash": tx_hash,
                    "block_number": tx_receipt["blockNumber"],
                    "gas_used": tx_receipt["gasUsed"],
                    "metadata": metadata
                }
            else:
                logger.error("Транзакция завершилась неудачно")
                return {
                    "success": False,
                    "transaction_hash": tx_hash,
                    "error": "Transaction failed"
                }
            
        except Exception as e:
            logger.error(f"Ошибка при минтинге NFT: {e}")
            raise
    
    
    async def _wait_for_transaction_receipt(self, tx_hash: str, timeout: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """Ожидает получения квитанции транзакции"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                tx_receipt = await self.client.web3.eth.get_transaction_receipt(tx_hash)
                if tx_receipt is not None:
                    return tx_receipt
            except TransactionNotFound:
                pass
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"Превышено время ожидания квитанции транзакции: {tx_hash}")
    