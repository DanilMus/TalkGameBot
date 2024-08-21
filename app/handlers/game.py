# 
# | Файл с настройкой базового роутера |
# 

# Библиотеки
from aiogram import F, Router
    
import logging

# Собственные модули
from app.handlers.game_handlers import preparing



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор

# Ставим Фильтр на действие только внутри групп и супергрупп
router.message.filter(F.chat.type.in_({"group", "supergroup"})) 
router.callback_query.filter(F.message.chat.type.in_({"group", "supergroup"})) 


# Подключение маршрутизаторов из папки game_handlers
router.include_routers(
    preparing.router
)