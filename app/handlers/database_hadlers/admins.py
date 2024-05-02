# 
# | CRUD на Admins |
# 


# библиотеки
from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import logging
from typing import Any, Callable, Dict, Awaitable

# свои модули
from app.dialog import Dialog
from app.database import DataBase
from app.callbacks import DataBaseCallbackFactory
from config import config



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_handlers.admins) # текст программы


# Outer-мидлварь на проверку прав доступа главного админа
class IsCreatorMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Можно подстраховаться и игнорировать мидлварь, если она установлена по ошибке НЕ на колбэки
        if not isinstance(event, CallbackQuery):
            logger.error("Мидлварь не установлена")
            return await handler(event, data)

        # Если это не админ или не главный админ, то не работаем с этим пользовалетелем
        if event.from_user.id != config.creator:
            await event.answer(dialog.take("no_rules"))
            return
        
        return await handler(event, data)

router.message.outer_middleware(IsCreatorMiddleware())
router.callback_query.outer_middleware(IsCreatorMiddleware())
        

# Класс для управления состояниями
class AdminsStates(StatesGroup):
    choosing_create = State()
    choosing_update = State()
    choosing_delete = State()


#
# | Create | 
#

# Обработчик для подготовки к добавлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(AdminsStates.choosing_create)

# Обработчик на добавление в Admins
@router.message(AdminsStates.choosing_create)
async def prepare_create_admins_handler(message: Message, state: FSMContext):
    id, username = message.text.split()

    async with DataBase.Admins() as admins:
        if await admins.create(id, username): # Проверка на то, что запись создана
            await message.answer(dialog.take("created"))
        else:
            await message.answer(dialog.take("error"))



# 
# | Read |
# 

# Обработчик на чтение Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_admins_handler(callback: CallbackQuery):
    async with DataBase.Admins() as admins:
        admins = await admins.read()

    if not admins: # Проверка на пустоту
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % admin for admin in admins])
    await callback.message.answer(response)



# 
# | Update |
# 

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(AdminsStates.choosing_update)

# Обработчик на обновление в Admins
@router.message(AdminsStates.choosing_update)
async def prepare_update_admins_handler(message: Message, state: FSMContext):
    id, username = message.text.split()

    async with DataBase.Admins() as admins:
        if await admins.update(id, username): # Проверка на выполнения действия
            await message.answer(dialog.take("updated"))
        else:
            await message.answer(dialog.take("error"))



# 
# | Delete |
# 

# Обработчик для подготовки к удалению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example_toDel"))
    await state.set_state(AdminsStates.choosing_delete)

# Обработчик на удаление в Admins
@router.message(AdminsStates.choosing_delete)
async def prepare_delete_admins_handler(message: Message, state: FSMContext):
    id, = message.text.split()

    async with DataBase.Admins() as admins:
        if await admins.delete(id): # Проверка на выполнения действия
            await message.answer(dialog.take("deleted"))
        else:
            await message.answer(dialog.take("error"))