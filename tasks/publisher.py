import random
import logging
from typing import Dict, Any

from tls_client.client import TLSClient


logger = logging.getLogger(__name__)


class Publisher:
        
    def __init__(self, tls_client: TLSClient, auth_cookies: Dict[str, str]):
        self.client = tls_client
        self.auth_cookies = auth_cookies
    
    
    async def upload_image(self, image_url: str) -> Dict[str, Any]:
        logger.info("Загрузка изображения на сервер")
        
        url = "https://app.mahojin.ai/api/upload/signed-url"
        
        payload = {
            "prefix": "images",
            "fileType": "image/png"
        }
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/ip/publish"
        }
        
        response = await self.client.post(
            url, 
            json=payload, 
            headers=headers, 
            cookies=self.auth_cookies
        )
        
        data = response.json()
        
        if "data" not in data or "imageId" not in data["data"]:
            logger.error(f"Ошибка при получении URL для загрузки: {data}")
            raise ValueError("Не удалось получить URL для загрузки")
        
        image_id = data["data"]["imageId"]
        read_url = data["data"]["readUrl"]
        
        logger.info(f"Получен URL для загрузки. Image ID: {image_id}")
        
        return {
            "imageId": image_id,
            "imageUrl": read_url
        }
    
    
    async def moderate_image(self, image_id: str, prompt: str) -> Dict[str, Any]:
        logger.info(f"Запрос модерации для изображения: {image_id}")
        
        url = f"https://app.mahojin.ai/api/images/moderations?imageId={image_id}"
        
        payload = {
            "prompt": prompt
        }
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/ip/publish"
        }
        
        response = await self.client.post(
            url, 
            json=payload, 
            headers=headers, 
            cookies=self.auth_cookies
        )
        
        data = response.json()
        
        if "key" not in data:
            logger.error(f"Ошибка при запросе модерации: {data}")
            raise ValueError("Не удалось запросить модерацию изображения")
        
        logger.info(f"Модерация прошла успешно. hasNSFW: {data.get('hasNSFW', False)}")
        
        return {
            "key": data["key"],
            "hasNSFW": data.get("hasNSFW", False)
        }
    
    
    async def prepare_metadata(self, image_data: Dict[str, Any], upload_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Подготовка метаданных для публикации")
        
        url = "https://app.mahojin.ai/api/metadata/image"
        
        prompt = image_data["prompt"]
        prompt_words = prompt.split()
        title = " ".join(random.sample(prompt_words, min(5, len(prompt_words))))
        title = title[0].upper() + title[1:]
        
        payload = {
            "domain": "0xb4D6411f44767a4C093CEFbf584cA9369849DB01",
            "image": {
                "imageId": image_data.get("requestId", ""),
                "imageUrl": image_data.get("imageUrl", ""),
                "previewImageUrl": "",
                "isPublished": False,
                "width": image_data["params"]["aspectRatio"]["width"],
                "height": image_data["params"]["aspectRatio"]["height"],
                "fromOutput": True,
                "resources": [
                    {
                        "modelId": image_data["params"]["checkpoint"]["modelId"],
                        "modelVersionId": image_data["params"]["checkpoint"]["modelVersionId"],
                        "modelName": "FLUX",
                        "modelVersionName": "Dev",
                        "modelType": "checkpoint"
                    }
                ],
                "createParam": {
                    "checkpoint": image_data["params"]["checkpoint"],
                    "resources": [
                        image_data["params"]["checkpoint"]
                    ],
                    "prompt": prompt,
                    "isMature": False,
                    "isDraftMode": False,
                    "aspectRatio": image_data["params"]["aspectRatio"],
                    "cfgScale": image_data["params"]["cfgScale"],
                    "steps": image_data["params"]["steps"],
                    "seed": image_data["seed"],
                    "quantity": 1
                },
                "isMatureThemed": False,
                "prompt": prompt,
                "cfgScale": image_data["params"]["cfgScale"],
                "steps": image_data["params"]["steps"],
                "seed": image_data["seed"],
                "ipType": "image",
                "refineSourceIds": [],
                "refineData": [],
                "thumbnailUrl": upload_data["imageUrl"]
            }
        }
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://app.mahojin.ai",
            "referer": "https://app.mahojin.ai/ip/publish"
        }
        
        response = await self.client.post(
            url, 
            json=payload, 
            headers=headers, 
            cookies=self.auth_cookies
        )
        data = response.json()
        
        if "metadataId" not in data or "metadataHash" not in data:
            logger.error(f"Ошибка при подготовке метаданных: {data}")
            raise ValueError("Не удалось подготовить метаданные")
        
        logger.info(f"Метаданные успешно подготовлены. ID: {data['metadataId']}")
        
        return {
            "metadataId": data["metadataId"],
            "metadataHash": data["metadataHash"],
            "metadata_url": f"https://app.mahojin.ai/api/metadata/image/{data['metadataId']}",
            "title": title,
            "prompt": prompt
        }
    
    
    async def publish_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        upload_data = await self.upload_image(image_data["imageUrl"])
        moderation_data = await self.moderate_image(upload_data["imageId"], image_data["prompt"])
        metadata = await self.prepare_metadata(image_data, upload_data)
        
        return {
            "upload": upload_data,
            "moderation": moderation_data,
            "metadata": metadata,
            "original": image_data
        }