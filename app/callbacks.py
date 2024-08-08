from aiogram.filters.callback_data import CallbackData

# Класс для управления колбэками в database_work.py и database_handlers
class DatabaseCallbackFactory(CallbackData, prefix= "db"):
    table: str
    action: str

# Класс для управления колбэками в game
class GameCallBackFactory(CallbackData, prefix= "game"):
    action: str