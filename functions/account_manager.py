import threading
import signal
import sys
import time
import random
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger

from tls_client.client import TLSClient
from evm.client import EVMClient
from evm.networks import Networks
from tasks.authenticator import Authenticator
from tasks.image_generator import ImageGenerator
from tasks.publisher import Publisher
from tasks.blockchain import BlockchainManager
from tasks.mahojin_task import MahojinTask
from tasks.promts import get_diverse_prompts


class AccountManager:
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.accounts = config_manager.accounts
        self.config = config_manager.config
        self.shutdown_event = threading.Event()
        self.threads = []
        self.next_runs = {}
        self.next_runs_lock = threading.Lock()
        
        signal.signal(signal.SIGINT, self.signal_handler)
    
    
    def signal_handler(self, sig, frame):
        """Обработчик сигнала для корректного завершения при Ctrl+C"""
        logger.info("Получен сигнал прерывания. Завершаем работу...")
        print("\n\033[93mПрограмма завершается, ожидайте...\033[0m")
        self.shutdown_event.set()
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        sys.exit(0)
    
    
    def validate_accounts(self) -> Tuple[bool, List[str]]:
        return self.config_manager.validate_accounts()
    
    
    def start_tasks(self):
        if not self.accounts:
            logger.warning("Нет аккаунтов для запуска")
            print("\033[91mНет аккаунтов для запуска. Добавьте аккаунты в файл accounts.csv\033[0m")
            return
        
        self.shutdown_event.clear()
        
        for i, account in enumerate(self.accounts):
            if self.shutdown_event.is_set():
                break
                
            thread = threading.Thread(
                target=self.account_task_loop,
                args=(account, i),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()
            
            time.sleep(random.uniform(1, 3))
        
        logger.info(f"Запущены задачи для {len(self.accounts)} аккаунтов")
        print(f"\033[92mЗапущены задачи для {len(self.accounts)} аккаунтов\033[0m")
        
        try:
            while not self.shutdown_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Остановка по команде пользователя")
            self.shutdown_event.set()
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join()
        
        self.threads = []
    
    
    def account_task_loop(self, account: Dict[str, str], account_index: int):
        private_key = account.get('private_key', '').strip()
        proxy = account.get('proxy', '').strip()
        
        if proxy.lower() == 'nan' or not proxy:
            proxy = None
        elif not (proxy.startswith('http://') or proxy.startswith('https://')):
            proxy = f"http://{proxy}"
        
        first_delay_min = self.config.get("first_generation_delay", {}).get("min_seconds", 10)
        first_delay_max = self.config.get("first_generation_delay", {}).get("max_seconds", 30)
        first_delay = random.uniform(first_delay_min, first_delay_max)
        
        logger.info(f"Аккаунт #{account_index+1}: Начинаем работу через {first_delay:.2f} секунд")
        print(f"\033[93mАккаунт #{account_index+1}: Начинаем работу через {first_delay:.2f} секунд\033[0m")
        time.sleep(first_delay)
        
        success = self.execute_task(private_key, proxy, account_index)
        
        while not self.shutdown_event.is_set():
            next_delay_min = self.config.get("subsequent_generation_delay", {}).get("min_seconds", 3600)
            next_delay_max = self.config.get("subsequent_generation_delay", {}).get("max_seconds", 7200)
            next_delay = random.uniform(next_delay_min, next_delay_max)
            
            logger.info(f"Аккаунт #{account_index+1}: Следующая задача через {next_delay/60:.2f} минут")
            
            next_time = time.strftime("%H:%M:%S", time.localtime(time.time() + next_delay))
            print(f"\033[93mАккаунт #{account_index+1}: Следующая задача в {next_time} (через {next_delay/60:.2f} минут)\033[0m")
            
            with self.next_runs_lock:
                self.next_runs[account_index] = {
                    "account_index": account_index,
                    "next_time": next_time,
                    "next_delay_minutes": next_delay/60
                }
            
            start_time = time.time()
            while time.time() - start_time < next_delay:
                if self.shutdown_event.is_set():
                    return
                time.sleep(1)
            
            success = self.execute_task(private_key, proxy, account_index)
    
    
    def execute_task(self, private_key: str, proxy: Optional[str], account_index: int) -> bool:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self._run_task(private_key, proxy, account_index))
            loop.close()
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Аккаунт #{account_index+1}: Ошибка выполнения задачи: {e}")
            print(f"\033[91mАккаунт #{account_index+1}: Ошибка выполнения задачи: {e}\033[0m")
            return False
    
    
    async def _run_task(self, private_key: str, proxy: Optional[str], account_index: int) -> Dict[str, Any]:
        logger.info(f"Аккаунт #{account_index+1}: Инициализация клиентов")
        
        tls_client = TLSClient(
            proxy=proxy,
            randomize_fingerprint=True
        )
        
        evm_client = EVMClient(
            private_key=private_key,
            network=Networks.MONAD,
            proxy=proxy
        )
        
        try:
            authenticator = Authenticator(tls_client)
            auth_success = await authenticator.authenticate(evm_client)
            
            if not auth_success:
                logger.error(f"Аккаунт #{account_index+1}: Аутентификация не удалась")
                print(f"\033[91mАккаунт #{account_index+1}: Аутентификация не удалась\033[0m")
                return {"success": False, "error": "Ошибка аутентификации"}
            
            image_generator = ImageGenerator(tls_client, authenticator.auth_cookies)
            publisher = Publisher(tls_client, authenticator.auth_cookies)
            blockchain_manager = BlockchainManager(evm_client)
            
            task = MahojinTask(tls_client, evm_client, authenticator, image_generator, publisher, blockchain_manager)
            result = await task.run()
            
            status = "успешно" if result.get("success", False) else "с ошибкой"
            logger.info(f"Аккаунт #{account_index+1}: Задача выполнена {status}")
            print(f"\033[{'92' if result.get('success', False) else '91'}mАккаунт #{account_index+1}: Задача выполнена {status}\033[0m")
            
            return result
            
        finally:
            await tls_client.close()
            