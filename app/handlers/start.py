# библиотеки
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from random import randint
# общение с пользователем
from app.start_dialog import Dialog

router = Router()
dialog = Dialog()

# начало
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear() # сбрасываение состояний

    await message.answer(dialog.take("start"))

# обработка ситуации, когда игрок посылает что-то не в тему
@router.message(F.text)
async def problem_handler(message: Message, state: FSMContext):
    await message.answer(dialog.take("problem"))

