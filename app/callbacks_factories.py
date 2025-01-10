"""| Файл для управления колбэками в других файлах |"""
# (Вынесен в отдельный файл, так как эти классы перескакивают с одного файла на другой,
# и чтобы их не записывать каждый раз одинаково, они прописаны здесь один раз и навсегда)

from aiogram.filters.callback_data import CallbackData

import importlib

import pydantic
from pydantic import field_validator
# Свои модули
from app.database import DataBase


class DatabaseCallbackFactory(CallbackData, prefix= "db"):
    """ Класс для управления колбэками в database_work.py и database_handlers
    """    
    table: str # Представляет из себя полное имя подкласса DataBase. Пример: app.database.DataBase.Gamers
    action: str
    read_page: int = 0

    @field_validator("table", mode= "before") # флаг before отмечает, что обработка ведется до преобразования входных данныъ
    @classmethod # Доступен на уровне класса, а не на уровне экземпляра
    def validate_and_convert_table(cls, value):
        if isinstance(value, type) and issubclass(value, DataBase._DataBase__Base): # isinstance(value, type) проверка, что value - класс
            # Преобразуем класс в строку
            return f"{value.__module__}.{value.__name__}"
        elif isinstance(value, str):
            # Проверка на то, что строка может быть преобразована в класс
            module_name, class_name = value.rsplit(".", 1)
            module = importlib.import_module(module_name)
            table_class = getattr(module, class_name, None)
            if not table_class or not issubclass(table_class, DataBase._DataBase__Base):
                raise ValueError(f"Неправильная таблица: {value}")
            return value
        raise ValueError(f"Таблица должна быть подклассом DataBase или строкой, а получено {value}")
    
    def get_table_class(self):
        # Десериализация: превращаем строку обратно в класс
        module_name, class_name = self.table.rsplit(".")
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    
    class Config:
        arbitrary_types_allowed = True # Разрешаем использовать сторонние классы


class GameCallbackFactory(CallbackData, prefix= "game"):
    """Класс для управления колбэками в game
    """    
    step: str
    question_or_action: bool = False
    no_or_yes: bool = False