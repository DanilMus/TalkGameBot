# библиотеки
from aiogram import types, Dispatcher
from aiogram.dispatcher.storage import FSMContext

# начало
async def start(message: types.Message, state: FSMContext):
    state.finish() # сбрасываение состояний

    await message.answer("Здарова")

# запуск обработка
async def register_start(dp: Dispatcher):
    dp.register_message_handler(start, commands= "start", state= "*")