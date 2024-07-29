# 
# |Обработчики для выбора с какой базой работать|
# 

# библиотеки
from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import logging
from typing import Any, Callable, Dict, Awaitable

# свои модули
from app.dialog import Dialog
from app.database import DataBase, async_session
from app.callbacks import DataBaseCallbackFactory
from app.handlers.database_handlers import gamers, admins, games, questions_actions, questions_actions_from_gamers, answers, participates
from config import config


# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_work) # текст программы
# Подключение роутеров на обработку CRUD у различных таблиц
router.include_routers(
    gamers.router,
    admins.router,
    games.router,
    questions_actions.router,
    questions_actions_from_gamers.router,
    answers.router,
    participates.router,
)



# Outer-мидлварь на проверку прав доступа
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
            # Если это не админ или не главный админ, то не работаем с этим пользовалетелем
            # (еще можно заметить, что можно использовать 2 способа достать id пользователя)
            if not await admins_db.is_exists(user.id) and event.from_user.id != config.creator:
                await event.answer(dialog.take("no_rules"))
                return
        
        return await handler(event, data)
# Подключение этой мидлвари на сообщения и на колбэки
router.message.outer_middleware(IsAdminMiddleware())
router.callback_query.outer_middleware(IsAdminMiddleware())




# Клавиатура для обработчиков db_handler и db_handler2
def kb_for_db_handler() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    # 1 строка
    kb.button(text= "Игроки", callback_data= DataBaseCallbackFactory(table= "Gamers", action= "start"))
    kb.button(text= "Админы", callback_data= DataBaseCallbackFactory(table= "Admins", action= "start"))
    kb.button(text= "Игры", callback_data= DataBaseCallbackFactory(table= "Games", action= "start"))
    # 2 строка
    kb.button(text= "Вопросы и Действия", callback_data= DataBaseCallbackFactory(table= "Questions_Actions", action= "start"))
    # 3 строка
    kb.button(text= "Вопросы и Действия от игроков", callback_data= DataBaseCallbackFactory(table= "Questions_Actions_From_Gamers", action= "start"))
    # 4 строка
    kb.button(text= "Ответы", callback_data= DataBaseCallbackFactory(table= "Answers", action= "start"))
    kb.button(text= "Участники", callback_data= DataBaseCallbackFactory(table= "Participates", action= "start"))
    # Отмечаем строки
    kb.adjust(3, 1, 1, 2)
    return kb


# 
# / Обработчики /
# 
# Обработчик для начала взаимодействия с базой
@router.message(Command("db"))
async def db_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(dialog.take("what_table"), reply_markup= kb_for_db_handler().as_markup())


# Обработчик при нажатии кнопки "Назад"
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "all" and F.action == "begin"))
async def db_handler2(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(dialog.take("what_table"), reply_markup= kb_for_db_handler().as_markup())



# Обработчик для предоставления команд на взаимодействие с таблицами
@router.callback_query(DataBaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, callback_data: DataBaseCallbackFactory, state: FSMContext):
    await state.clear()
    table = callback_data.table

    kb = InlineKeyboardBuilder()
    if table == "Admins" or table == "Questions_Actions": # Только у этих таблиц есть возможность редактирования
        kb.button(text= "Добавить", callback_data= DataBaseCallbackFactory(table= table, action= "create"))
        kb.button(text= "Прочитать", callback_data= DataBaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Обновить", callback_data= DataBaseCallbackFactory(table= table, action= "update"))
        kb.button(text= "Удалить", callback_data= DataBaseCallbackFactory(table= table, action= "delete"))
        kb.button(text= "Назад", callback_data= DataBaseCallbackFactory(table= "all", action= "begin"))
        kb.adjust(4)
    else:
        kb.button(text= "Прочитать", callback_data= DataBaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Назад", callback_data= DataBaseCallbackFactory(table= "all", action= "begin"))

    
    await callback.message.edit_text(dialog.take("what_action") % table, reply_markup= kb.as_markup())
