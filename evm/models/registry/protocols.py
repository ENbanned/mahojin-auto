from typing import Dict
from ..protocol import Protocol

class MonadProtocols:
    # APRIORI = Protocol(
    #     address="0xb2f82D0f38dc453D596Ad40A37799446Cc89274A",
    #     name="aPriori",
    #     abi_filename="aPriori.json"
    # )


    
    _by_address: Dict[str, Protocol] = {}

    @classmethod
    def get_by_address(cls, address: str) -> Protocol:
        """Получает протокол по его адресу"""
        if not cls._by_address:
            for attr_name in dir(cls):
                if attr_name.startswith('_'):
                    continue
                protocol = getattr(cls, attr_name)
                if isinstance(protocol, Protocol):
                    cls._by_address[protocol.address.lower()] = protocol
        
        address = address.lower()
        if address not in cls._by_address:
            raise ValueError(f"Неизвестный протокол с адресом {address}")
        
        return cls._by_address[address]