# 
# | Файл для управления колбэками в других файлах |
# 
# (Вынесен в отдельный файл, так как эти классы перескакивают с одного файла на другой,
# и чтобы их не записывать каждый раз одинаково, они прописаны здесь один раз и навсегда)

from aiogram.filters.callback_data import CallbackData

# Класс для управления колбэками в database_work.py и database_handlers
class DatabaseCallbackFactory(CallbackData, prefix= "db"):
    table: str
    action: str

# Класс для управления колбэками в game
class GameCallbackFactory(CallbackData, prefix= "game"):
    action: str