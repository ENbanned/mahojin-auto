from typing import Dict
from ..token import Token

class MonadTokens:

    # MON = Token(
    #     address="0x0000000000000000000000000000000000000000",
    #     name="Monad",
    #     symbol="MON",
    #     decimals=18,
    #     is_native=True
    # )

    # WMON = Token(
    #     address="0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701",
    #     name="Wrapped Monad",
    #     symbol="WMON",
    #     decimals=18,
    #     abi_filename="monad_wrap_eth.json"
    # )



    _by_address: Dict[str, Token] = {}


    @classmethod
    def get_by_address(cls, address: str) -> Token:
        if not cls._by_address:
            for attr_name in dir(cls):
                if attr_name.startswith('_'):
                    continue
                token = getattr(cls, attr_name)
                if isinstance(token, Token):
                    cls._by_address[token.address.lower()] = token
        
        address = address.lower()
        if address not in cls._by_address:
            raise ValueError(f"Неизвестный токен с адресом {address}")
        
        return cls._by_address[address]