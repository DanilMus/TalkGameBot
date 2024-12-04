"""|Обработчики для выбора с какой базой работать|"""


from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import logging
from typing import Any, Callable, Dict, Awaitable

# свои модули
from app.messages import Messages
from app.database import DataBase, async_session
from app.callbacks_factories import DatabaseCallbackFactory
from app.handlers.database_handlers import admins, gamers, chats, questions_actions, questions_actions_from_gamers, games, participants, answers
from config.config_reader import config


"""Переменные для оргиназации работы"""
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # текст программы


"""Фильтры и Мидлвари"""
# Ставим Фильтр на действие только внутри частных чатов
router.message.filter(F.chat.type == "private") 
router.callback_query.filter(F.message.chat.type == "private") 

# Мидлварь на проверку прав доступа
class IsAdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]

        async with async_session() as session:
            admins_db = DataBase.Admins(session)
            # Если это админ или главный админ, то работаем с этим пользовалетелем
            # (еще можно заметить, что можно использовать 2 способа достать id пользователя)
            if await admins_db.is_exists(user.id) or event.from_user.id == config.id_owner.get_secret_value():
                return await handler(event, data)
     
        await event.answer(messages.take("no_rules"))
        return
    
# Подключение этой внутренней мидлвари на сообщения и на колбэки
router.message.middleware(IsAdminMiddleware())
router.callback_query.middleware(IsAdminMiddleware())



"""/ Обработчики /"""
# Обработчик для начала взаимодействия с базой
@router.message(Command("db"))
async def db_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(messages.take("what_table"), reply_markup= kb_for_db_handler().as_markup())


# Обработчик при нажатии кнопки "Назад"
@router.callback_query(DatabaseCallbackFactory.filter(F.table == "all" and F.action == "begin"))
async def db_handler2(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(messages.take("what_table"), reply_markup= kb_for_db_handler().as_markup())


# Клавиатура для обработчиков db_handler и db_handler2
def kb_for_db_handler() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    # 1 строка
    kb.button(text= "Игроки", callback_data= DatabaseCallbackFactory(table= DataBase.Gamers, action= "start"))
    kb.button(text= "Админы", callback_data= DatabaseCallbackFactory(table= DataBase.Admins, action= "start"))
    kb.button(text= "Чаты", callback_data= DatabaseCallbackFactory(table= DataBase.Chats, action= "start"))
    # 2 строка
    kb.button(text= "Вопросы и Действия", callback_data= DatabaseCallbackFactory(table= DataBase.Questions_Actions, action= "start"))
    # 3 строка
    kb.button(text= "Вопросы и Действия от игроков", callback_data= DatabaseCallbackFactory(table= DataBase.Questions_Actions_From_Gamers, action= "start"))
    # 4 строка
    kb.button(text= "Игры", callback_data= DatabaseCallbackFactory(table= DataBase.Games, action= "start"))
    kb.button(text= "Участники", callback_data= DatabaseCallbackFactory(table= DataBase.Participants, action= "start"))
    kb.button(text= "Ответы", callback_data= DatabaseCallbackFactory(table= DataBase.Answers, action= "start"))
    # Отмечаем строки
    kb.adjust(3, 1, 1, 3)
    return kb



# Обработчик для предоставления команд на взаимодействие с таблицами
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory, state: FSMContext):
    await state.clear()
    table = callback_data.table

    kb = InlineKeyboardBuilder()
    if table == "Admins" or table == "Questions_Actions": # Только у этих таблиц есть возможность редактирования
        kb.button(text= "Добавить", callback_data= DatabaseCallbackFactory(table= table, action= "create"))
        kb.button(text= "Прочитать", callback_data= DatabaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Обновить", callback_data= DatabaseCallbackFactory(table= table, action= "update"))
        kb.button(text= "Удалить", callback_data= DatabaseCallbackFactory(table= table, action= "delete"))
        kb.button(text= "Назад", callback_data= DatabaseCallbackFactory(table= "all", action= "begin"))
        kb.adjust(4)
    else:
        kb.button(text= "Прочитать", callback_data= DatabaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Назад", callback_data= DatabaseCallbackFactory(table= "all", action= "begin"))

    
    await callback.message.edit_text(messages.take("what_action") % table, reply_markup= kb.as_markup())



"""Подключение роутеров с обработчиками таблиц базы"""
router.include_routers(
    gamers.router,
    admins.router,
    chats.router,
    questions_actions.router,
    questions_actions_from_gamers.router,
    games.router,
    answers.router,
    participants.router,
)