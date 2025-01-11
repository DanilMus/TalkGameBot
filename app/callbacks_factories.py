"""| Файл для управления колбэками в других файлах |"""
# (Вынесен в отдельный файл, так как эти классы перескакивают с одного файла на другой,
# и чтобы их не записывать каждый раз одинаково, они прописаны здесь один раз и навсегда)

from aiogram.filters.callback_data import CallbackData

import importlib
import logging
from pydantic import field_validator
# Свои модули
from app.database import DataBase


logger = logging.getLogger(__name__)

class DatabaseCallbackFactory(CallbackData, prefix= "db"):
    """ Класс для управления колбэками в database_work.py и database_handlers
    """   
    action: str 
    table: str = "nothing" # Представляет из себя полное имя подкласса DataBase. Пример: app.database.DataBase.Gamers
    read_page: int = 0

    # Обработка того, как работаем с переменной table
    @field_validator("table", mode= "before") # флаг before отмечает, что обработка ведется до преобразования входных данныъ
    @classmethod # Доступен на уровне класса, а не на уровне экземпляра
    def validate_and_convert_table(cls, value):
        if isinstance(value, type) and issubclass(value, DataBase._DataBase__Base): # isinstance(value, type) проверка, что value - класс
            return f"{value.__name__}"
        elif isinstance(value, str): # тут соотвественно проверка, что значение - это строка
            if not getattr(DataBase, value, False) and value != "nothing":
                logger.error(f"Неправильная таблица: {value}")
            return value
        logger.error(f"Таблица должна быть подклассом DataBase или строкой, а получено {value}")
    
    def get_table_class(self):
        return getattr(DataBase, self.table)

    class Config:
        arbitrary_types_allowed = True # Разрешаем использовать сторонние классы


class GameCallbackFactory(CallbackData, prefix= "game"):
    """Класс для управления колбэками в game
    """    
    step: str
    question_or_action: bool = False
    no_or_yes: bool = False