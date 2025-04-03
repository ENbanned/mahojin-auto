import os
import sys
import threading
from typing import Dict, Callable

class UIManager:
        
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.shutdown_event = threading.Event()
    
    
    def show_header(self):
        header = r"""
 ███╗   ███╗ █████╗ ██╗  ██╗ ██████╗      ██╗██╗███╗   ██╗
 ████╗ ████║██╔══██╗██║  ██║██╔═══██╗     ██║██║████╗  ██║
 ██╔████╔██║███████║███████║██║   ██║     ██║██║██╔██╗ ██║
 ██║╚██╔╝██║██╔══██║██╔══██║██║   ██║██   ██║██║██║╚██╗██║
 ██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝╚█████╔╝██║██║ ╚████║
 ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚═╝╚═╝  ╚═══╝
"""
        os.system('cls' if sys.platform.startswith('win') else 'clear')
        
        print("\033[36m" + header + "\033[0m")
        print("\033[92m{:=^80}\033[0m".format(""))
        print("\033[93m{:^80}\033[0m".format("Telegram: https://t.me/enbanends_home"))
        print("\033[93m{:^80}\033[0m".format("@enbanned"))
        print("\033[92m{:=^80}\033[0m".format(""))
        print("\n\033[96mГенератор и минтер изображений Mahojin AI\033[0m")
        print("\033[90m{:-^80}\033[0m".format(""))
    
    
    def show_menu(self):
        """Выводит меню программы"""
        print("\n\033[95mВыберите действие:\033[0m")
        print("\033[94m1. Проверить, готова ли программа к запуску")
        print("2. Запустить программу")
        print("3. Закрыть программу\033[0m")
        print("\033[90m{:-^80}\033[0m".format(""))
    
    
    def start_interface(self, action_handlers: Dict[str, Callable]):
        while not self.shutdown_event.is_set():
            self.show_header()
            self.show_menu()
            
            try:
                choice = input("\033[95mВведите номер действия: \033[0m")
                
                if choice == '1':
                    action_handlers.get('validate')()
                elif choice == '2':
                    action_handlers.get('start')()
                elif choice == '3':
                    action_handlers.get('exit')()
                    break
                else:
                    print("\033[91mНеверный выбор. Пожалуйста, выберите 1, 2 или 3.\033[0m")
                    import time
                    time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n\033[93mПрограмма завершена пользователем (Ctrl+C)\033[0m")
                self.shutdown_event.set()
                break
            except Exception as e:
                from loguru import logger
                logger.error(f"Ошибка в интерфейсе: {e}")
                print(f"\033[91mПроизошла ошибка: {e}\033[0m")
                import time
                time.sleep(2)
                