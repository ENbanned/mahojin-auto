import random
import time
import logging
import asyncio
from typing import Dict, Any

from tls_client.client import TLSClient

logger = logging.getLogger(__name__)


class ImageGenerator:
    
    def __init__(self, tls_client: TLSClient, auth_cookies: Dict[str, str]):
        self.client = tls_client
        self.auth_cookies = auth_cookies
        self.models = [
            {"modelId": "p4PgTp_bT9OxMzlnV7UeZQ", "modelVersionId": "qePX9z3iSJKZjEbFU8AYzw", "name": "FLUX", "version": "Dev"}, 
            {"modelId": "vUGcx92eTwKKfk7MUaAVoA", "modelVersionId": "5e61_C85TxCfYMIoqQH2bw", "name": "XMAG", "version": "1.0"}, 
            {"modelId": "vCKbjB-mTnWjQUCdMW2QCw", "modelVersionId": "mC_Twa9fQnyLQNQNF8n4lg", "name": "Visions", "version": "1.0"}
        ]
        self.aspect_ratios = [
            {"label": "Square", "width": 1024, "height": 1024},
            {"label": "Landscape", "width": 1280, "height": 720},
            {"label": "Portrait", "width": 720, "height": 1280}
        ]
    
    
    def get_random_model(self) -> Dict[str, str]:
        model = random.choice(self.models)
        return {
            "modelId": model["modelId"],
            "modelVersionId": model["modelVersionId"]
        }
    
    
    def get_random_aspect_ratio(self) -> Dict[str, Any]:
        return random.choice(self.aspect_ratios)
    
    
    async def generate_image(self, prompt: str) -> Dict[str, Any]:
        logger.info(f"Генерация изображения с prompt: '{prompt}'")
        
        url = "https://app.mahojin.ai/api/generate-image"
        
        json_data = {
            'checkpoint': {
                'modelId': 'p4PgTp_bT9OxMzlnV7UeZQ',
                'modelVersionId': 'qePX9z3iSJKZjEbFU8AYzw',
            },
            'resources': [],
            'prompt': prompt,
            'isMature': False,
            'isDraftMode': False,
            'aspectRatio': {
                'label': 'Square',
                'width': 1024,
                'height': 1024,
            },
            'cfgScale': 3.5,
            'steps': 30,
            'seed': '-1',
            'quantity': 1,
        }
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/images"
        }
        
        response = await self.client.post(
            url, 
            json=json_data, 
            headers=headers, 
            cookies=self.auth_cookies
        )
        
        data = response.json()
        
        if "request" not in data or "requestId" not in data["request"]:
            logger.error(f"Ошибка при запросе генерации изображения: {data}")
            raise ValueError("Не удалось начать генерацию изображения")
        
        request_id = data["request"]["requestId"]
        logger.info(f"Изображение в процессе генерации, ID запроса: {request_id}")
        
        return await self.wait_for_generation(request_id, prompt, json_data)
    
    
    async def check_generation_status(self, request_id: str) -> Dict[str, Any]:
        url = "https://app.mahojin.ai/api/generate-image/requests/sync-state"
        
        payload = {
            "requestIds": [request_id]
        }
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/images"
        }
        
        response = await self.client.post(
            url, 
            json=payload, 
            headers=headers, 
            cookies=self.auth_cookies
        )
        
        return response.json()
    
    
    async def wait_for_generation(self, request_id: str, prompt: str, params: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = await self.check_generation_status(request_id)
            
            if "requests" not in status_data or not status_data["requests"]:
                logger.error(f"Ошибка при проверке статуса: {status_data}")
                await asyncio.sleep(5)
                continue
            
            request = status_data["requests"][0]
            state = request.get("state", "UNKNOWN")
            
            if state == "DONE":
                logger.info(f"Изображение успешно сгенерировано за {int(time.time() - start_time)} секунд")
                
                jobs = request.get("jobs", [])
                if jobs and "imageUrl" in jobs[0]:
                    image_url = jobs[0]["imageUrl"]
                    image_seed = jobs[0].get("seed", "")
                    
                    return {
                        "requestId": request_id,
                        "state": state,
                        "imageUrl": image_url,
                        "prompt": prompt,
                        "seed": image_seed,
                        "params": params
                    }
            
            elif state == "FAILED":
                logger.error(f"Генерация изображения завершилась ошибкой: {request}")
                raise ValueError(f"Ошибка генерации изображения: {request.get('error', 'Неизвестная ошибка')}")
            
            logger.debug(f"Статус генерации: {state}, ожидаем...")
            await asyncio.sleep(5)
        
        logger.error(f"Время ожидания генерации изображения истекло ({timeout} сек)")
        raise TimeoutError(f"Время ожидания генерации изображения истекло ({timeout} сек)")
    