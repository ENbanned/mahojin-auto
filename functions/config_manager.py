import os
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Tuple
from loguru import logger

class ConfigManager:
    
    def __init__(self, files_dir="files"):
        self.files_dir = files_dir
        self.accounts_csv = "accounts.csv"
        self.config_json = "config.json"
        
        self.ensure_files_exist()
        self.config = self.load_config()
        self.accounts = self.load_accounts()
    
    
    def ensure_files_exist(self) -> None:
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)
            logger.info(f"Создана папка {self.files_dir}")
        
        config_path = os.path.join(self.files_dir, self.config_json)
        if not os.path.exists(config_path):
            default_config = {
                "first_generation_delay": {
                    "min_seconds": 60,
                    "max_seconds": 600
                },
                "subsequent_generation_delay": {
                    "min_seconds": 43200, 
                    "max_seconds": 86400   
                }
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Создан файл конфигурации {config_path} с настройками по умолчанию")
        
        accounts_path = os.path.join(self.files_dir, self.accounts_csv)
        if not os.path.exists(accounts_path):
            with open(accounts_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['private_key', 'proxy'])
            logger.info(f"Создан файл аккаунтов {accounts_path}")
    
    
    def load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(self.files_dir, self.config_json)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Ошибка в формате файла {config_path}. Создаем файл с настройками по умолчанию.")
            default_config = {
                "first_generation_delay": {
                    "min_seconds": 10,
                    "max_seconds": 30
                },
                "subsequent_generation_delay": {
                    "min_seconds": 3600,
                    "max_seconds": 7200
                }
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    
    def load_accounts(self) -> List[Dict[str, str]]:
        accounts_path = os.path.join(self.files_dir, self.accounts_csv)
        try:
            df = pd.read_csv(accounts_path)
            if 'private_key' in df.columns:
                df['private_key'] = df['private_key'].str.strip()
            if 'proxy' in df.columns:
                df['proxy'] = df['proxy'].str.strip()
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Ошибка при чтении файла аккаунтов {accounts_path}: {e}")
            return []
        
        
    def reload_accounts(self) -> List[Dict[str, str]]:
        self.accounts = self.load_accounts()
        return self.accounts
    
    
    def validate_accounts(self) -> Tuple[bool, List[str]]:
        if not self.accounts:
            return False, ["Нет аккаунтов в файле accounts.csv"]
        
        errors = []
        for i, account in enumerate(self.accounts):
            if 'private_key' not in account or not account['private_key']:
                errors.append(f"Аккаунт #{i+1}: Отсутствует приватный ключ")
                continue
                
            private_key = account['private_key'].strip()
            if not all(c in '0123456789abcdefABCDEF' for c in private_key) or len(private_key) != 64:
                errors.append(f"Аккаунт #{i+1}: Некорректный формат приватного ключа")
            
            if 'proxy' in account and account['proxy'] and not str(account['proxy']).lower().strip() == 'nan':
                proxy = str(account['proxy']).strip()
                if not (
                    proxy.startswith('http://') or proxy.startswith('https://') or
                    ':' in proxy
                ):
                    errors.append(f"Аккаунт #{i+1}: Некорректный формат прокси ({proxy})")
        
        return len(errors) == 0, errors
    