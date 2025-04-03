import random
from typing import Dict, Any
from loguru import logger

from tls_client.client import TLSClient
from evm.client import EVMClient
from .authenticator import Authenticator
from .image_generator import ImageGenerator
from .publisher import Publisher
from .blockchain import BlockchainManager
from tasks.promts import get_diverse_prompts


class MahojinTask:
    
    def __init__(self, 
                 tls_client: TLSClient, 
                 evm_client: EVMClient,
                 authenticator: Authenticator,
                 image_generator: ImageGenerator,
                 publisher: Publisher,
                 blockchain_manager: BlockchainManager):
        self.tls_client = tls_client
        self.evm_client = evm_client
        self.authenticator = authenticator
        self.image_generator = image_generator
        self.publisher = publisher
        self.blockchain_manager = blockchain_manager
    
    
    async def run(self) -> Dict[str, Any]:        
        try:
            if not self.authenticator.auth_cookies:
                logger.error("Аутентификация не выполнена")
                return {"success": False, "error": "Ошибка аутентификации"}
            
            try:
                logger.info("Пытаемся заклеймить поинты")
                point_data = await self.tls_client.post(
                    url='https://app.mahojin.ai/api/point/claim',
                    json={},
                )
                
                if point_data.status_code == 200:
                    point_data_json = point_data.json()
                    current_points = point_data_json.get("point", 0)
                    logger.info(f"Поинты успешно заклеймлены. Текущее количество поинтов: {current_points}")
                    
                    if current_points < 40:
                        logger.info(f"Недостаточно поинтов для выполнения задачи (требуется 40, текущее: {current_points}). Ожидаем следующего захода.")
                        return {
                            "success": True,
                            "skip_reason": "insufficient_points",
                            "current_points": current_points,
                            "required_points": 40,
                            "point_data": point_data_json
                        }
                else:
                    logger.warning(f"Ошибка при клейме поинтов: {point_data.status_code}, {point_data.text}")
            except Exception as e:
                logger.error(f"Ошибка при клейме поинтов: {e}")
            
            logger.info("Начало процесса генерации изображения")
            prompt = random.choice(get_diverse_prompts())
            image_data = await self.image_generator.generate_image(prompt)
            
            logger.info("Начало процесса публикации изображения")
            publish_data = await self.publisher.publish_image(image_data)
            
            logger.info("Начало процесса минтинга NFT")
            blockchain_result = await self.blockchain_manager.mint_image_nft(publish_data["metadata"])
            
            result = {
                "success": blockchain_result["success"],
                "image": {
                    "url": image_data["imageUrl"],
                    "prompt": prompt,
                    "seed": image_data["seed"]
                },
                "blockchain": {
                    "transaction_hash": blockchain_result.get("transaction_hash"),
                    "block_number": blockchain_result.get("block_number"),
                    "token_id": blockchain_result.get("token_id")
                },
                "metadata": publish_data["metadata"]
            }
                        
            return result
            
        except Exception as e:
            logger.exception(f"Ошибка при выполнении задачи: {e}")
            return {"success": False, "error": str(e)}
        