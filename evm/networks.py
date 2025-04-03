from dataclasses import dataclass
from typing import Optional, Union, Dict, Any

@dataclass
class Network:
    name: str
    chain_id: int
    rpc_url: str
    explorer_url: Optional[str] = None
    token_symbol: str = "ETH"
    token_name: str = "Ethereum"
    token_decimals: int = 18
    
    def __post_init__(self):
        if self.explorer_url and not self.explorer_url.endswith("/"):
            self.explorer_url += "/"

class Networks:

    MONAD = Network(
        name="Story",
        chain_id=1514, 
        rpc_url="https://evm-rpc.story.mainnet.dteam.tech",
        explorer_url="https://explorer.story.foundation",
        token_symbol="IP",
        token_name="IP Token",
        token_decimals=18
    )
    