from random import randint
import logging

logger = logging.getLogger(__name__)

class Dialog():
    start = {
            "start": ["Привет!", "Рад тебя видеть!", "Круто, что ты здесь!", "Вау, привет!"], 
            "problem": ["Такой команды нет", "Такого действия нет"],
        }
    database_work = {
        "error": ["Произошла какая-то ошибка"],
        "what_table": ["Выбери с какой таблицей хочешь поработать:"],
        "what_action": ["Что хочешь сделать с таблицей %s"],
        "base_close": ["База закрыта"],
        "base_empty": ["База пуста"],
        "admin_example": ["Укажи ID и nickname.\nПример: 1 Ivan"],
        "example_toDel": ["Укажи ID. \nПример: 1"],
        "admin_created": ["Админ успешно добавлен"],
        "admin_read": ["ID:%s\tnickname:%s"],
        "admin_updated": ["Админ успешно изменен"],
        "admin_deleted": ["Админ успешно удален"],
    }

    def __init__(self, dialog: dict):
        self.dialog = dialog

    def take(self,  s: str):
        msg = self.dialog.get(s)

        if not msg:
            logger.error(f"Не удалось найти диалог у {s}")
            return "К сожалению обнаружена проблема с диалогами. Я уже сообщил об этом разработчику. Если проблема сохраниться напишите @snecht"

        return msg[randint(0, len(msg)-1)]
    
