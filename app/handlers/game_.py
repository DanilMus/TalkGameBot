# 
# |Самая главная часть - игра|
# 

# Библиотеки
from aiogram import F, Router
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aiogram.filters import Command, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
    

import logging
from random import randint

# Собственные модули
from app.dialog import Dialog
from database import db
from app.callbacks import GameCallBackFactory



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.game) # класс с диалогами

# Ставим Фильтр на действие только внутри групп и супергрупп
router.message.filter(F.chat.type.in_({"group", "supergroup"})) 

# Фильтр на владельца чата
class IsChatOwner(BaseFilter):
    async def __call__(self, message: Message):
        member = await message.chat.get_member(message.from_user.id)

        return member.status is ChatMemberStatus.CREATOR
        
# Класс для управления состояниями
class GameStates(StatesGroup):
    choosing_participants = State()
    choosing_rounds = State()
    round_begining = State()
    prepare_answering = State()
    answering = State()
    end_answering = State()
    assesment = State()







# Для понимания, кто будет участвовать 
async def starting_choosing_participants_handler(message_or_event, state: FSMContext):
    await state.clear() # сбрасываение состояний

    # kb = InlineKeyboardBuilder()
    # kb.button(text= "Я", callback_data= GameCallBackFactory(action= "i"))
    # kb.button(text= "Закончили", callback_data= GameCallBackFactory(action= "end"))
    # kb.adjust(1)
    
    await message_or_event.answer(dialog.take("participants"))
    await state.set_state(GameStates.choosing_participants)
    await state.update_data(participants= {})



# Обработчик на добавление в чат
@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed= JOIN_TRANSITION
    )
)
async def game_handler(event: ChatMemberUpdated, state: FSMContext):
    await starting_choosing_participants_handler(event, state)

# Обработчик на команду game, т.е. на самое главное - начало игры
@router.message(IsChatOwner(), Command("game"))
async def game_handler(message: Message, state: FSMContext):
    await starting_choosing_participants_handler(message, state)


# Обработчик на участвующих
@router.message(F.text.lower() == "я", StateFilter(GameStates.choosing_participants))
async def choosing_participants_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data["participants"].get(message.from_user.full_name, False):
        data["participants"][message.from_user.full_name] = 0
        await message.answer("%s теперь участвует в игре" % message.from_user.full_name)

# Обработчик на завершения выбора участвующих
@router.message(IsChatOwner(), F.text.lower() == "закончили", StateFilter(GameStates.choosing_participants))
async def ending_choosing_participants_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    
    db.connect()
    members = len(data["participants"])
    rounds = db.questions_actions.rounds(members)
    db.close()

    if members < 2:
        return await message.answer("Игроков должно быть больше 1")

    if rounds:
        await state.update_data(rounds= rounds)
        await state.set_state(GameStates.choosing_rounds)
        return await message.answer(dialog.take("start") % str(rounds))
    
    await message.answer(dialog.take("problem_withRounds"))
    logger.info(f"Не удалось провести игру, слишком много людей: {members}")


async def round_begining_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(whos_turn= list(data["participants"].keys()))
    await message.answer("Раунд начинается! Как будете гововы напишите что-нибудь...")

# Обработчик на количество раундов, которое хочет провести игрок
@router.message(IsChatOwner(), StateFilter(GameStates.choosing_rounds))
async def choosing_rounds_handler(message: Message, state: FSMContext):
    user_data = await state.get_data()
    msg = message.text

    try:
        new_rounds = int(msg)
        if 0 < new_rounds <= user_data["rounds"]: # Количество раундов больше 0 и не больше возможного
            await state.update_data(rounds= new_rounds)
            await state.update_data(questions_actions= db.questions_actions.questions_actions())
            await state.set_state(state= GameStates.prepare_answering)
            await message.answer(dialog.take("starting_game"))
            await round_begining_handler(message, state)
        else:
            await message.answer(dialog.take("problem_with_rounds_int") % user_data["rounds"])

    except:
        await message.answer(dialog.take("problem_with_rounds_text"))


@router.message(StateFilter(GameStates.prepare_answering))
async def prepare_answering_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.answer(f"{data["whos_turn"][-1]} напишите соотвественно, что вы хотите Вопрос или Действие")
    await state.set_state(GameStates.answering)


@router.message(StateFilter(GameStates.answering), F.text.lower().in_(["вопрос", "действие"]))
async def answering_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    
    if message.from_user.full_name != data["whos_turn"][-1]:
        return await message.answer("Решает другой игрок")

    msg = message.text
    msg = "question" if msg.lower() == "вопрос" else "action"

    
    question_action = data["questions_actions"][msg]
    if len(question_action)-1 != 0:
        num_question_action = randint(0, len(question_action)-1)
    else:
        num_question_action = 0

    await message.answer(question_action.pop(num_question_action))
    await state.set_data(data)
    await message.answer("Как закончите с ответом напишите что угодно")
    await state.set_state(GameStates.end_answering)
    

@router.message(StateFilter(GameStates.end_answering))
async def end_answering_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer("Теперь я попрошу других участников оценить, игрок ответил на вопрос или сделал нужное действие: Да или Нет")
    await state.set_state(GameStates.assesment)
    await state.update_data(new_whos_turn= list(data["participants"].keys()))

@router.message(StateFilter(GameStates.assesment), F.text.lower().in_(["да", "нет"]))
async def assesment_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.from_user.full_name == data["whos_turn"][-1]:
        return await message.answer("Вы не можете оценить сами себя")
    
    data["participants"][data["whos_turn"][-1]] += 1 if message.text.lower() == "да" else -1
    await message.answer("Ваш ответ принят")

    for i in range(len(data["new_whos_turn"])):
        if data["new_whos_turn"][i] == message.from_user.full_name:
            data["new_whos_turn"].pop(i)
            break

    await state.set_data(data)

    if len(data["new_whos_turn"]) == 1:
        data["whos_turn"].pop()
        await state.set_data(data)
        if data["whos_turn"]:
            await state.set_state(GameStates.prepare_answering)
            await message.answer(f"Все ответы засчитаны. \n{data["whos_turn"][-1]} ваша очередь, напишите что-угодно, как будете готовы.")
        else:
            data["rounds"] -= 1
            if data["rounds"] < 1:
                await message.answer("Игра закончена.")
                await message.answer(f"Счет: \n{"\n".join(key + " " + str(val) for key, val in data["participants"].items())}")



# Обрабочик ситуации, когда игрок посылает что-то не в тему
@router.message(F.text)
async def problem_handler(message: Message, state: FSMContext):
    await message.answer(dialog.take("problem"))


