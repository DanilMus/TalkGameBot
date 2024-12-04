"""| Файл для управления колбэками в других файлах |"""
# (Вынесен в отдельный файл, так как эти классы перескакивают с одного файла на другой,
# и чтобы их не записывать каждый раз одинаково, они прописаны здесь один раз и навсегда)

from aiogram.filters.callback_data import CallbackData
# Свои модули
from app.database import DataBase

# Класс для управления колбэками в database_work.py и database_handlers
class DatabaseCallbackFactory(CallbackData, prefix= "db"):
    table: DataBase
    action: str
    read_page: int = 0

    class Config:
        arbitrary_types_allowed = True

# Класс для управления колбэками в game
class GameCallbackFactory(CallbackData, prefix= "game"):
    step: str
    question_or_action: bool = False
    no_or_yes: bool = False