# 
# | Файл с обработчиками запуска игры и подсчета тех, кто будет участвовать |
# 

# Библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
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
# Фильтр для просмотра, что отвечает тот, чья очередь
class AnswerOfWhosTurnFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        return callback.from_user.username == data["whos_turn"]

# Фильтр для просмотра, что ответ получен от других, т.е. не от того, чья очередь
class AnswerOfOthersTurnFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        return callback.from_user.username != data["whos_turn"]


# 
# Обработчики 
# 
# Самое начало, где пишется какой раунд и где происходит перенос к выбору вопроса или действия
@router.callback_query(StateFilter(GameStates.starting_round), GameCallbackFactory.filter(F.step == "starting_round"))
async def starting_round_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(messages.take("starting_round") % data["round"])
    await question_or_action_handler(callback, state)


# Выдача выбора, на что будет отвечать тот, чья очередь
async def question_or_action_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    kb = InlineKeyboardBuilder()
    kb.button(text= "Вопрос", callback_data= GameCallbackFactory(step= "question_action", question_or_action= False))
    kb.button(text= "Действие", callback_data= GameCallbackFactory(step= "question_action", question_or_action= True))

    await callback.message.answer(messages.take("question_or_action") % data["whos_turn"], reply_markup= kb.as_markup())


# Выдача вопроса или действия с возможностью закончить ответ
@router.callback_query(StateFilter(GameStates.starting_round), GameCallbackFactory.filter(F.step == "question_action"), AnswerOfWhosTurnFilter())
async def question_action_handler(callback: CallbackQuery, callback_data: GameCallbackFactory, state: FSMContext):
    data = await state.get_data()

    kb = InlineKeyboardBuilder()
    kb.button(text= "Закончил/а", callback_data= GameCallbackFactory(step= f"end_question_action", question_or_action= callback_data.question_or_action))

    await callback.message.edit_text(messages.take(callback_data.step) % (data["whos_turn"], data["questions_actions"][callback_data.question_or_action].pop()), reply_markup= kb.as_markup())


# Это уже по сути голосование, где другие игроки оценивают, как ответил тот, чья очередь
@router.callback_query(StateFilter(GameStates.starting_round), GameCallbackFactory.filter(F.step == "end_question_action"), AnswerOfWhosTurnFilter())
async def end_question_action_handler(callback: CallbackQuery, callback_data: GameCallbackFactory, state: FSMContext):
    data = await state.get_data()

    kb= InlineKeyboardBuilder()
    kb.button(text= "Да", callback_data= GameCallbackFactory(step= "no_yes_question_action", no_or_yes= True))
    kb.button(text= "Нет", callback_data= GameCallbackFactory(step= "no_yes_question_action", no_or_yes= False))

    await callback.message.edit_text(messages.take(f"end_{("question", "action")[callback_data.question_or_action]}") % data["whos_turn"], reply_markup= kb.as_markup())
    # Создаем пустой список, в котором будут те, кто ответил на Да и Нет
    data["others_turn"] = []
    await state.update_data(data)


# То, где обрабатывается конец ответа, раунда и игры и где происходят соответствующие перенаправления на нужные функции
@router.callback_query(StateFilter(GameStates.starting_round), GameCallbackFactory.filter(F.step == "no_yes_question_action"), AnswerOfOthersTurnFilter())
async def no_yes_question_action_handler(callback: CallbackQuery, callback_data: GameCallbackFactory, state: FSMContext):
    await callback.answer(messages.take(callback_data.step) % callback.from_user.username)

    data = await state.get_data()
    data["others_turn"].append(callback.from_user.username)
    data["participants"][callback.from_user.username] += callback_data.no_or_yes
    await state.set_data(data)

    # Если собрали все ответы, от всех игроков, кроме того, чья очередь
    if len(data["others_turn"]) == len(data["participants"]) - 1:
        await callback.message.edit_text(messages.take("end_"+callback_data.step))
        try:
            await state.update_data(whos_turn= next(data["whos_turn_iter"]))
            await question_or_action_handler(callback, state)
        except StopIteration: # если больше некого брать в итераторе
            if data["round"] + 1 <= data["rounds"]: # Если некому участвовать, то начинаем новый раунд
                data["whos_turn_iter"] = iter(data["participants"])
                data["whos_turn"] = next(data["whos_turn_iter"])
                data["round"] += 1
                await state.set_data(data)
                await starting_round_handler(callback, state)
            else: # Если же некому участвовать и всее раунды закончились, то заканчиваем игру
                await end_game_handler(callback, state)


# Конец и выдача результатов
async def end_game_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sorted_participants = dict(sorted(data["participants"].items(), key= lambda x: x[1], reverse= True))

    ans, i = messages.take("end_game_1"), 0
    for gamer, points in sorted_participants.items():
        i += 1
        ans += messages.take("end_game_2") % (i, gamer, points)
        

    await callback.message.answer(ans)
    await state.clear()