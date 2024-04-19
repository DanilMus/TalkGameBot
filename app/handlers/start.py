# Библиотеки
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
# Общение с пользователем
from app.dialog import Dialog
from app.database import db

router = Router() # маршрутизатор
dialog = Dialog(Dialog.start) # класс с диалогами

# Обработчик на команду start
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # Добавляем нового игрока в базу, если его нет
    db.connect()
    if not db.gamers.is_exists(message.from_user.id):
        db.gamers.create(message.from_user.id, message.from_user.username)
    db.close()

    await state.clear() # сбрасываение состояний

    await message.answer(dialog.take("start"))

# Обрабочик ситуации, когда игрок посылает что-то не в тему
@router.message(F.text)
async def problem_handler(message: Message, state: FSMContext):
    await message.answer(dialog.take("problem"))

