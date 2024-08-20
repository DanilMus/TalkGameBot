# 
# | Файл с обработчиками запуска игры и подсчета тех, кто будет участвовать |
# 

# Библиотеки
from aiogram import F, Router
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aiogram.filters import Command, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
    

import logging

# Собственные модули
from app.messages import Messages
from app.database import DataBase, async_session
from app.callbacks_factories import GameCallBackFactory
from app.states import GameStates



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # класс с диалогами

# Ставим Фильтр на действие только внутри групп и супергрупп
router.message.filter(F.chat.type.in_({"group", "supergroup"})) 
router.callback_query.filter(F.chat.type.in_({"group", "supergroup"})) 

# Фильтр на владельца чата
class IsChatOwnerFilter(BaseFilter):
    async def __call__(self, message: Message):
        member = await message.chat.get_member(message.from_user.id)

        return member.status is ChatMemberStatus.CREATOR

    

# 
# Подготовка закончилась, начинается игра
# 
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


# Для понимания, кто будет участвовать 
async def starting_choosing_participants_handler(message_or_event, state: FSMContext):
    await state.clear() # сбрасываение состояний

    kb = InlineKeyboardBuilder()
    kb.button(text= "Я", callback_data= GameCallBackFactory(action= "i"))

    kb2 = ReplyKeyboardBuilder()
    kb2.button(text= "Закончили")
    
    await message_or_event.answer(messages.take("participants"), reply_markup= kb.as_markup())
    await message_or_event.answer(messages.take("participants_chosen"), reply_markup= kb2.as_markup(resize_keyboard= True))
    await state.update_data(participants= {})
    await state.set_state(GameStates.choosing_participants)


# Обработчик на участвующих (тех, кто нажал на |Я| и теперь участвует в игре)
@router.callback_query(GameCallBackFactory.filter(F.action == "i"))
async def choosing_participants_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data["participants"].get(callback.from_user.full_name, False):
        data["participants"][callback.from_user.username] = 0
        await callback.message.answer(messages.take("new_participant") % callback.from_user.username)


# Обработчик на окончание в игре
@router.message(IsChatOwnerFilter(), StateFilter(GameStates.choosing_participants), F.text.lower() == "закончили")
async def ending_choosing_participants_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    
    async with async_session() as session:
        questions_actions = DataBase.Questions_Actions(session)
        members = len(data["participants"])
        rounds = await questions_actions.rounds(members)

    if members < 2:
        return await message.answer((messages.take("problem_with_participants")))

    if rounds:
        await state.update_data(rounds= rounds)
        return await message.answer(messages.take("start") % str(rounds))
    
    await message.answer(messages.take("problem_withRounds"))
    logger.info(f"Не удалось провести игру, слишком много людей: {members}")
