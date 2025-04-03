import sys
import time
import colorama
import signal
from loguru import logger

from functions.logger_setup import setup_logging
from functions.config_manager import ConfigManager
from functions.ui_manager import UIManager
from functions.account_manager import AccountManager

colorama.init()


def validate_action(account_manager):
    account_manager.config_manager.reload_accounts()
    account_manager.accounts = account_manager.config_manager.accounts
    
    is_valid, errors = account_manager.validate_accounts()
    
    if is_valid:
        print("\033[92mВсе аккаунты и прокси валидны. Программа готова к запуску!\033[0m")
    else:
        print("\033[91mОбнаружены ошибки в конфигурации:\033[0m")
        for error in errors:
            print(f"\033[91m - {error}\033[0m")
    
    input("\n\033[95mНажмите Enter для продолжения...\033[0m")


def start_action(account_manager):
    account_manager.config_manager.reload_accounts()
    account_manager.accounts = account_manager.config_manager.accounts
    
    is_valid, errors = account_manager.validate_accounts()
    
    if not is_valid:
        print("\033[91mОбнаружены ошибки в конфигурации:\033[0m")
        for error in errors:
            print(f"\033[91m - {error}\033[0m")
        print("\033[91mИсправьте ошибки перед запуском.\033[0m")
        input("\n\033[95mНажмите Enter для продолжения...\033[0m")
        return
    
    print("\033[92mЗапуск программы...\033[0m")
    account_manager.start_tasks()


def exit_action(account_manager):
    """Действие при выборе пункта выхода"""
    print("\033[93mЗавершение программы...\033[0m")
    account_manager.shutdown_event.set()


def main():
    setup_logging()
    logger.info("Запуск программы")
    
    def global_signal_handler(sig, frame):
        logger.info("Получен сигнал прерывания на уровне main")
        print("\n\033[93mПрограмма завершена пользователем (Ctrl+C)\033[0m")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, global_signal_handler)
    
    try:
        config_manager = ConfigManager()
        ui_manager = UIManager(config_manager)
        account_manager = AccountManager(config_manager)
        
        action_handlers = {
            'validate': lambda: validate_action(account_manager),
            'start': lambda: start_action(account_manager),
            'exit': lambda: exit_action(account_manager)
        }
        ui_manager.start_interface(action_handlers)
        
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
        print("\n\033[93mПрограмма завершена пользователем (Ctrl+C)\033[0m")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")
        print(f"\n\033[91mНеобработанная ошибка: {e}\033[0m")
        sys.exit(1)
    finally:
        logger.info("Программа завершена")
        print("\033[93mПрограмма завершена\033[0m")


if __name__ == "__main__":
    main()