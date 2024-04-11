from random import randint

class Dialog():
    def __init__(self):
        self.dialog = {
            "start": ["Привет!", "Рад тебя видеть!", "Круто, что ты здесь!", "Вау, привет!"], 
            "problem": ["Такой команды нет", "Такого действия нет"]
        }

    def take(self, s: str):
        msg = self.dialog.get(s, ["Не удалось найти текст диалога"])
        return msg[randint(0, len(msg)-1)]