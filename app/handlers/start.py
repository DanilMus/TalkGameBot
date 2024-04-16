# библиотеки
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
# общение с пользователем
from app.dialog import Dialog

router = Router() # маршрутизатор
dialog = Dialog(Dialog.start) # класс с диалогами

# обработчик на команду start
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear() # сбрасываение состояний

    await message.answer(dialog.take("start"))

# обрабочик ситуации, когда игрок посылает что-то не в тему
@router.message(F.text)
async def problem_handler(message: Message, state: FSMContext):
    await message.answer(dialog.take("problem"))

