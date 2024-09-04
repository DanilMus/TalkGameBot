# 
# | Файл с обработчиками запуска игры и подсчета тех, кто будет участвовать |
# 

# Библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
    
import logging

# Собственные модули
from app.messages import Messages
from app.callbacks_factories import GameCallbackFactory
from app.states import GameStates


#
# Переменные для оргиназации работы
#
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # класс с диалогами

# 
# Фильтры
# 
class AnswerOfWhosTurnFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        logger.error(data)
        return callback.from_user.username == data["whos_turn"]

class AnswerOfOthersTurnFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        return callback.from_user.username != data["whos_turn"]


# 
# Обработчики 
# 
@router.callback_query(GameCallbackFactory.filter(F.step == "starting_round"), StateFilter(GameStates.starting_round))
async def starting_round_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer(messages.take("starting_round") % data["round"])
    await question_or_action_handler(callback, state)


async def question_or_action_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    kb = InlineKeyboardBuilder()
    kb.button("Вопрос", callback_data= GameCallbackFactory(step= "question_action", question_or_action= False))
    kb.button("Действие", callback_data= GameCallbackFactory(step= "question_action", question_or_action= True))

    await callback.message.answer(messages.take("question_or_action") % data["whos_turn"], reply_markup= kb.as_markup())



@router.callback_query(AnswerOfWhosTurnFilter(), GameCallbackFactory.filter(F.step == "question_action"), StateFilter(GameStates.starting_round))
async def question_action_handler(callback: CallbackQuery, callback_data: GameCallbackFactory, state: FSMContext):
    data = await state.get_data()

    kb = InlineKeyboardBuilder()
    kb.button("Закончил/а", callback_data= GameCallbackFactory(step= f"end_question_action", question_or_action= callback_data.question_or_action))

    await callback.message.edit_text(messages.take(callback_data.step) % (data["whos_turn"], data["questions_actions"][callback_data.question_or_action].pop()), reply_markup= kb.as_markup(kb))


@router.callback_query(AnswerOfWhosTurnFilter(), GameCallbackFactory.filter(F.step == "end_question_action"), StateFilter(GameStates.starting_round))
async def end_question_action_handler(callback: CallbackQuery, callback_data: GameCallbackFactory, state: FSMContext):
    data = await state.get_data()

    kb= InlineKeyboardBuilder()
    kb.button("Да", callback_data= GameCallbackFactory(step= "no_yes_question_action", no_or_yes= True))
    kb.button("Нет", callback_data= GameCallbackFactory(step= "no_yes_question_action", no_or_yes= False))

    await callback.message.edit_text(messages.take(f"end_{("question", "action")[callback_data.question_or_action]}" % (data["whos_turn"])), reply_markup= kb.as_markup())
    # Создаем пустой список, в котором будут те, кто ответил на Да и Нет
    data["others_turn"] = []
    state.update_data(data)


@router.callback_query(AnswerOfOthersTurnFilter, GameCallbackFactory.filter(F.step == "no_yes_question_action"), StateFilter(GameStates.starting_round))
async def no_yes_question_action_handler(callback: CallbackQuery, callback_data: GameCallbackFactory, state: FSMContext):
    await callback.answer(messages.take(callback_data.step) % callback.from_user.username)

    data = await state.get_data()
    data["others_turn"].append(callback.from_user.username)

    if len(data["others_turn"]) == len(data["participants"]) - 1:
        data["whos_turn_i"] += 1

        if data["whos_turn_i"] < len(data["participants"]): # Если еще есть кому участвовать, продолжаем раунд
            data["whos_turn"] = next(data["whos_turn_iter"])
            await question_or_action_handler(callback, state)
        elif data["round"] + 1 <= data["rounds"]: # Если некому участвовать, то начинаем новый раунд
            data["round"] += 1
            await starting_round_handler(callback, state)
        else: # Если же некому участвовать и всее раунды закончились, то заканчиваем игру
            await end_game_handler(callback, state)


async def end_game_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sorted_participants = dict(sorted(data["participants"].items(), key= lambda x: x[1], reverse= True))

    ans, i = messages.take("end_game_1"), 0
    for gamer, points in sorted_participants.items():
        i += 1
        ans += messages.take("end_game_2") % (i, gamer, points)
        

    await callback.message.answer(ans)