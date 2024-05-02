# 
# | Самая главная часть - игра |
# 

# Библиотеки
from aiogram import F, Router
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aiogram.filters import Command, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
    

import logging
from random import randint

# Собственные модули
from app.dialog import Dialog
from app.database import db, DataBase
from app.callbacks import GameCallBackFactory



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.game) # класс с диалогами

# Ставим Фильтр на действие только внутри групп и супергрупп
router.message.filter(F.chat.type.in_({"group", "supergroup"})) 
router.callback_query.filter(F.chat.type.in_({"group", "supergroup"})) 

# Фильтр на владельца чата
class IsChatOwnerFilter(BaseFilter):
    async def __call__(self, message: Message):
        member = await message.chat.get_member(message.from_user.id)

        return member.status is ChatMemberStatus.CREATOR

# Класс для управления состояниями
class GameStates(StatesGroup):
    choosing_participants = State()
    

# 
# Подготовка закончилась, начинается игра
# 
# Для понимания, кто будет участвовать 
async def starting_choosing_participants_handler(message_or_event, state: FSMContext):
    await state.clear() # сбрасываение состояний

    # Занесение в базу данных о создании игры
    async with DataBase.Games() as games:
        await games.create_start()



    kb = InlineKeyboardBuilder()
    kb.button(text= "Я", callback_data= GameCallBackFactory(action= "i"))

    kb2 = ReplyKeyboardBuilder()
    kb2.button(text= "Закончили")
    
    await message_or_event.answer(dialog.take("participants"), reply_markup= kb.as_markup())
    await message_or_event.answer(dialog.take("participants_chosen"), reply_markup= kb2.as_markup(resize_keyboard= True))
    await state.update_data(participants= {})
    await state.set_state(GameStates.choosing_participants)


# Обработчик на добавление в чат
@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed= JOIN_TRANSITION
    )
)
async def game_handler(event: ChatMemberUpdated, state: FSMContext):
    await starting_choosing_participants_handler(event, state)


# Обработчик на команду game, т.е. на самое главное - начало игры
@router.message(IsChatOwnerFilter(), Command("game"))
async def game_handler(message: Message, state: FSMContext):
    await starting_choosing_participants_handler(message, state)


# Обработчик на участвующих
@router.callback_query(GameCallBackFactory.filter(F.action == "i"))
async def choosing_participants_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data["participants"].get(callback.from_user.full_name, False):
        data["participants"][callback.from_user.username] = 0
        await callback.message.answer(dialog.take("new_participant") % callback.from_user.username)


@router.message(IsChatOwnerFilter(), StateFilter(GameStates.choosing_participants), F.text.lower() == "закончили")
async def ending_choosing_participants_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    
    await db.connect()
    members = len(data["participants"])
    rounds = db.questions_actions.rounds(members)
    await db.close()

    if members < 2:
        return await message.answer((dialog.take("problem_with_participants")))

    if rounds:
        await state.update_data(rounds= rounds)
        return await message.answer(dialog.take("start") % str(rounds))
    
    await message.answer(dialog.take("problem_withRounds"))
    logger.info(f"Не удалось провести игру, слишком много людей: {members}")
