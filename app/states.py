# 
# | Файл с состояниями |
# 

from aiogram.fsm.state import State, StatesGroup

# Состояния файла admins.py
class DatabaseStates(StatesGroup):
    choosing_create = State()
    choosing_update = State()
    choosing_delete = State()


# Состояния папки game
class GameStates(StatesGroup):
    choosing_participants = State()
    choosing_rounds = State()
    starting_round = State()