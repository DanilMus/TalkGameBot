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
from app.callbacks_factories import GameCallbackFactory
from app.states import GameStates



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # класс с диалогами

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
    kb.button(text= "Я", callback_data= GameCallbackFactory(step= "i_will"))

    kb2 = ReplyKeyboardBuilder()
    kb2.button(text= "Закончили")
    
    await message_or_event.answer(messages.take("participants"), reply_markup= kb.as_markup())
    await message_or_event.answer(messages.take("participants_chosen"), reply_markup= kb2.as_markup(resize_keyboard= True))
    await state.update_data(participants= {})
    await state.set_state(GameStates.choosing_participants)


# Обработчик на участвующих (тех, кто нажал на |Я| и теперь участвует в игре)
@router.callback_query(StateFilter(GameStates.choosing_participants), GameCallbackFactory.filter(F.step == "i_will"))
async def choosing_participants_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if data["participants"].get(callback.from_user.username, True):
        data["participants"][callback.from_user.username] = 0
        await callback.message.answer(messages.take("new_participant") % callback.from_user.username)


# Обработчик на окончание выбора игроков, которые будут учавствовать, в игре
@router.message(IsChatOwnerFilter(), StateFilter(GameStates.choosing_participants), F.text.lower() == "закончили")
async def ending_choosing_participants_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    
    async with async_session() as session:
        questions_actions = DataBase.Questions_Actions(session)
        members = len(data["participants"])
        max_rounds = await questions_actions.count_max_rounds(members)
        
        # Если игроков недостаточно
        if members < 2:
            return await message.answer((messages.take("problem_with_participants")))

        # Если не удастся организовать ни один раунд
        if max_rounds == 0:
            logger.info(f"Не удалось провести игру, слишком много людей: {members}")
            await message.answer(messages.take("problem_withRounds"))
        # Если раунды есть, заносим их макс кол-во
        await state.update_data(rounds= max_rounds)

        # Клавиатура для быстрого ответа на кол-во раундов
        kb = ReplyKeyboardBuilder()
        for i in range(1, max_rounds + 1):
            if i > 7:
                break
            kb.button(text= str(i))
        await message.answer(messages.take("start") % max_rounds, reply_markup= kb.as_markup(resize_keyboard= True))    

        await state.set_state(GameStates.choosing_rounds)
    


# Обработчик на кол-во раундов, которое будет выбрано
@router.message(IsChatOwnerFilter(), StateFilter(GameStates.choosing_rounds), F.text.isdigit())
async def choosing_rounds_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    if not(0 < int(message.text) <= data["rounds"]):
        return await message.answer(messages.take("problem_with_rounds_int") % data["rounds"])

    data["rounds"] = int(message.text.strip())
    async with async_session() as session:
        questions_actions = DataBase.Questions_Actions(session)
        data["questions_actions"] = await questions_actions.make_rounds(data["rounds"], len(data["participants"]))

    kb = InlineKeyboardBuilder()
    kb.button(text= "Погнали!", callback_data= GameCallbackFactory(step= "starting_round"))
    await message.answer(messages.take("starting_game"), reply_markup= kb.as_markup())

    await state.set_state(GameStates.starting_round)
    data["whos_turn_iter"] = iter(data["participants"])
    data["whos_turn"] = next(data["whos_turn_iter"])
    data["round"] = 1
    await state.update_data(data)