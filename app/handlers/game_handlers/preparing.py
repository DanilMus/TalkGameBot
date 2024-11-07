"""| Файл с обработчиками запуска игры и подсчета тех, кто будет участвовать |"""

from aiogram import F, Router
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery, TelegramObject
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



"""
Переменные для оргиназации работы
"""
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # класс с диалогами


"""
Фильтры
"""
class IsChatOwnerFilter(BaseFilter):
    """Фильтр на владельца чата
    """    
    async def __call__(self, event: TelegramObject):
        """Собственно сама проверка

        Args:
            event (TelegramObject): тут будет либо класс Message, либо CallbackQuery

        Returns:
            bool: правда или ложь, что тот, кто написал, владелец чата
        """        
        if isinstance(event, Message): # если event это Message
            member = await event.chat.get_member(event.from_user.id)
        else: # если event это CallbackQuery
            member = await event.message.chat.get_member(event.from_user.id)
        
        return member.status is ChatMemberStatus.CREATOR
    

"""
Клавиатуры (если используются больше чем в 1 обработчике)
"""
def keyboard_voating_participants() -> InlineKeyboardBuilder:
    """Клавиатура для определения участников игр

    Returns:
        InlineKeyboardBuilder: простая клавиатура с кнопками "Я" (типо буду участвовать) и "Закончили" (чтобы определить, когда заканчиваем выбор участников)
    """    
    kb = InlineKeyboardBuilder()
    kb.button(text= "Я", callback_data= GameCallbackFactory(step= "i_will"))
    kb.button(text= "Закончили", callback_data= GameCallbackFactory(step= "ending_choosing"))
    kb.adjust(1)
    return kb

    
"""
Обработчики
""" 
@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed= JOIN_TRANSITION
    )
)
async def game_handler(event: ChatMemberUpdated, state: FSMContext):
    """Обработчик на добавление в чат
    """    
    await starting_choosing_participants_handler(event, state)


@router.message(Command("game"))
async def game_handler(message: Message, state: FSMContext):
    """Обработчик на команду game, т.е. на самое главное - начало игры
    """    
    await starting_choosing_participants_handler(message, state)
    message.chat.mem


async def starting_choosing_participants_handler(message_or_event, state: FSMContext):
    """По сути продолжение двух функций game_handler, чтобы не дублировать в каждом из них все
    """    
    await state.clear() # сбрасываение состояний
    
    await message_or_event.answer(messages.take("participants"), reply_markup= keyboard_voating_participants().as_markup())
    await state.update_data(participants= []) # Делаем список тех, кто будет участвовать в игре, не все ведь могут хотеть участвовать в чате
    await state.set_state(GameStates.choosing_participants)


    async with async_session() as session:
        # Проверяем существование чата в базе
        chats = DataBase.Chats(session)
        if not await chats.is_exists(message_or_event.chat.id):
            chat = await chats.create(
                id= message_or_event.chat.id, 
                name= message_or_event.chat.full_name,
                type= message_or_event.chat.get_members_count()
                )




@router.callback_query(GameStates.choosing_participants, GameCallbackFactory.filter(F.step == "i_will"))
async def choosing_participants_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик на участвующих (тех, кто нажал на |Я| и теперь участвует в игре)
    """    
    data = await state.get_data()
    
    async with async_session() as session:
        # Проверяем существование игрока в базе
        gamers = DataBase.Gamers(session)
        gamer = await gamers.is_exists(callback.from_user.id)
        if not gamer:
            gamer = await gamers.create(id= callback.from_user.id, username= callback.from_user.username)
        
        if gamer not in data["participants"]:
            data["participants"].append(gamer)
            await callback.message.answer(messages.take("new_participant") % callback.from_user.username) # Сообщаем о присоединении нового участника



@router.callback_query(GameStates.choosing_participants, IsChatOwnerFilter(), GameCallbackFactory.filter(F.step == "ending_choosing"))
async def ending_choosing_participants_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик на окончание выбора игроков, которые будут учавствовать, в игре
    """    
    await callback.message.edit_text(messages.take("ending_choosing")) # Сообщаем, что выбор игроков закончен
    data = await state.get_data()
    
    # Подключаемся к базе, чтобы создать нужный пул из вопросов и действий к игре
    async with async_session() as session:
        questions_actions = DataBase.Questions_Actions(session)
        num_participants = len(data["participants"])

        # Если игроков недостаточно, посылаем сообщение об этом
        if num_participants < 2:
            return await callback.message.edit_text((messages.take("problem_with_participants")), reply_markup= keyboard_voating_participants().as_markup())
        

        max_rounds = await questions_actions.count_max_rounds(num_participants) # Смотрим, сколько раундов вообще можем организовать
        
        # Если не удастся организовать ни один раунд
        if max_rounds == 0:
            logger.info(f"Не удалось провести игру, слишком много людей: {num_participants}")
            return await callback.message.edit_text(messages.take("problem_withRounds"))
        
        # Если раунды есть, заносим их макс кол-во
        await state.update_data(rounds= max_rounds)

        # Клавиатура для быстрого ответа на кол-во раундов
        kb = ReplyKeyboardBuilder()
        for i in range(1, max_rounds + 1):
            if i > 7:
                break
            kb.button(text= str(i))
        
        # Даем игроку выбрать количество раундов
        await callback.message.answer(messages.take("start") % max_rounds, reply_markup= kb.as_markup(resize_keyboard= True))    
        await state.set_state(GameStates.choosing_rounds)
    


@router.message(GameStates.choosing_rounds, IsChatOwnerFilter(), F.text.isdigit()) # Проверяем, что получаем число
async def choosing_rounds_handler(message: Message, state: FSMContext):
    """Обработчик на кол-во раундов, которое будет выбрано
    """    
    await message.answer(message.take("preparing_game"))

    data = await state.get_data()

    # Если раундов отрицательное число, то сообщаем об этом
    if not(0 < int(message.text) <= data["rounds"]):
        return await message.answer(messages.take("problem_with_rounds_int") % data["rounds"])

    # Если с раундами все нормально, то заносим их в состояния и получаем пул вопросов и действий для игры
    data["rounds"] = int(message.text.strip())
    async with async_session() as session:
        questions_actions = DataBase.Questions_Actions(session)
        data["questions_actions"] = await questions_actions.make_rounds(data["rounds"], len(data["participants"]))

        # Отмечаем в базе, что игра началась
        games = DataBase.Games(session)
        game = await games.create(id_chat= message.chat.id, rounds= data["rounds"])

        # Отмечаем в базе подключение игрока к игре
        participants = DataBase.Participants(session)
        for i in range(len(data["participants"])):
            data["participants"][i] = await participants.create(
                id_game= game.id, 
                id_gamer= data["participants"][i].id
                )

    # Подготовливаем данные для round.py
    await state.set_state(GameStates.starting_round)
    data["whos_turn"] = 0
    data["round"] = 1
    await state.set_data(data)

    # Посылаем игроку информацию о готовности к игре
    kb = InlineKeyboardBuilder()
    kb.button(text= "Погнали!", callback_data= GameCallbackFactory(step= "starting_round"))
    await message.edit_text(messages.take("starting_game"), reply_markup= kb.as_markup())