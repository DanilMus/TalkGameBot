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
        "no_rules": ["У вас нет нужных прав для выполнения этой команды"],
    }
    game = {
        "participants": ["Спасибо, что добавили меня в чат! Буду рад устроить вам игру! \n\n Тот, кто хочет участвовать в игре, пусть напишет: я или Я \n\nКак закончите, пусть владец чата отправит: Закончили или закончили."],
        "start": ["Количество раундов, которое я могу для вас провести не больше %s. \n\nПрошу владельца чата указать количество раундов, которые будет проведено:"],
        "problem_withRounds": ["Прошу прощения, но вас слишком много для того, чтобы я мог провести игру. Я уже сообщил создателю, что не хватает вопросов для игр. Будем надяться, что он не будет лениться."], 
        "problem": ["Сожалею, ничем не могу помочь"],
        "problem_with_rounds_text": ["Введите целое число, пожалуйста"],
        "problem_with_rounds_int": ["Введите число от 0 до %s"],
        "starting_game": ["Что ж начнем нашу игру!"],
    }

    class database_handlers():
        common = {
            "error": ["Произошла какая-то ошибка"],
            "base_empty": ["База пуста"],
            "example_toDel": ["Укажи ID. \nПример: 1"],
        }

        gamers = {
            "read": ["ID: <code>%s</code> \tnickname: %s"],
        }
        gamers.update(common)

        admins = {
            "example": ["Укажи ID и nickname.\nПример: 1 Ivan"],
            "created": ["Админ успешно добавлен"],
            "read": ["ID: <code>%s</code> \tnickname: %s"],
            "updated": ["Админ успешно изменен"],
            "deleted": ["Админ успешно удален"],
        }
        admins.update(common)

        games = {
            "read": ["ID: <code>%s</code>  game_start: %s game_end:"],
        }
        games.update(common)

        questions_actions = {
            "example": ["Укажи вопрос или действие (0, 1) ли это, категорию и само задание.\n\nПример: 0_философия_В чем смысл жизни? ИЛИ 1_смартфон_Покажи последнее фото"],
            "example_toUpdate": ["Укажи ID, вопрос или действие (0, 1) ли это, категорию и само задание.\n\nПример: 1234_0_философия_В чем смысл жизни? ИЛИ 1234_1_смартфон_Покажи последнее фото"],
            "created": ["Задание успешно добавлено"],
            "read": ["ID: <code>%s</code>  ID_admin: <code>%s</code>  \nquestion_or_action: %s  \ncategory: %s \ntask: %s\n"],
            "updated": ["Задание успешно изменено"],
            "deleted": ["Задание успешно удалено"],
        }
        questions_actions.update(common)

        questions_actions_from_gamers = {
            "read": ["ID: <code>%s</code>  ID_gamer: <code>%s</code>  \ntask: %s\n"],
        }
        questions_actions_from_gamers.update(common)
        
        answers = {
            "read": ["ID: <code>%s</code>  ID_game: <code>%s</code>  ID_gamer: <code>%s</code> \nID_question_action: <code>%s</code> \nfrom_game_or_gamer: %s \nanswer_start: %s answer_end: %s score: %s\n"],
        }
        answers.update(common)

        participates = {
            "read": ["ID: <code>%s</code>  ID_game: <code>%s</code>  ID_gamer: <code>%s</code> \nconnection_time: %s disconnection_time: %s\n"],
        }
        participates.update(common)



    def __init__(self, dialog: dict):
        self.dialog = dialog

    def take(self,  s: str) -> str:
        msg = self.dialog.get(s)

        if not msg:
            logger.error(f"Не удалось найти диалог у {s}")
            return "К сожалению обнаружена проблема с диалогами. Я уже сообщил об этом создателю. Если проблема сохраниться напишите @snecht"

        return msg[randint(0, len(msg)-1)]
    
