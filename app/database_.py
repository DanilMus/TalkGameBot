# 
# Взаимодействие с БД
# 

# Библиотеки
import mysql.connector
import mysql.connector.cursor
import logging
from abc import ABC # Для создания абстрактных классов
from datetime import datetime

# Свои модули
from config import config


logger = logging.getLogger(__name__) # логирование событий
# Класс для взаимодействия с базой
class DataBase():
    # База для взаимодействиями с таблицами
    class __Base(ABC):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor, table_name: str):
            self.connection = connection
            self.cursor = cursor
            self.table_name = table_name

        
        # Подключение и отключение автоматически и ассинхронно с использованием with
        async def __aenter__(self):
            try:
                self.connection = mysql.connector.connect(user= config.db_user, 
                                                                password= config.db_password,
                                                                host= config.db_host,
                                                                database=config.db_name,
                                                                charset= "utf8")
                self.cursor = self.connection.cursor()
                return self
            except Exception as ex:
                logger.error(f"Проблема с БД: {ex}")
                return None
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.cursor.close()
            self.connection.close()


        # Для чтения
        async def r(self, query: str, data = ()):
            try: 
                self.cursor.execute(query, data)
                return self.cursor.fetchall() 
            except mysql.connector.Error as err:
                logger.error(f"Проблема с подключением к базе: {err}")
                return None
            except Exception as ex:
                logger.error(f"Что-то пошло не так: {ex}")
                return None
        
        # Для записи
        async def w(self, query: str, data = ()):
            try:
                self.cursor.execute(query, data)
                self.connection.commit()
                return True
            except mysql.connector.Error as err:
                logger.error(f"Проблема с подключением к базе: {err}")
                return False
            except Exception as ex:
                logger.error(f"Что-то пошло не так: {ex}")
                return False
            
        # Функция для чтения (она у всех одинаковая, как ни странно)
        async def read(self):
            return await self.r(f"SELECT * FROM {self.table_name}")
        
        # Функция для удаления (она тоже у всех одинаковая)
        async def delete(self, id):
            return await self.w(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))
    # База для взаимодействия с таблицами Gamers, Admins
    class __PeopleBase(__Base, ABC):
        # Метод для проверки существования в таблице
        async def is_exists(self, id):
            try: 
                query = (f"SELECT * FROM {self.table_name} WHERE id = %s")
                data = (id, )
                self.cursor.execute(query, data)
                return self.cursor.fetchone() is not None
            except mysql.connector.Error as err:
                logger.error(f"Проблема с подключением к базе: {err}")
                return None
            except Exception as ex:
                logger.error(f"Что-то пошло не так: {ex}")
                return None

        # Функция для добавления человека
        async def create(self, id, username):
            return await self.w(f"INSERT INTO {self.table_name} (id, username) VALUES (%s, %s)", (id, username))

        # Функция для обновления информации об человеке
        async def update(self, id, username):
            return await self.w(f"UPDATE {self.table_name} SET username = %s WHERE id = %s", (username, id))


    # Класс для взаимодействия с таблицей Gamers
    class Gamers(__PeopleBase):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Gamers")

    # Класс для взаимодействия с таблицей Admins
    class Admins(__PeopleBase):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Admins")

    # Класс для взаимодействия с таблицей Games
    class Games(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Games")
        
        # Функция для добавления начала игры
        async def create_start(self):
            timing = datetime.now()
            await self.w(f"INSERT INTO {self.table_name} (start_or_end, timing) VALUES (%s, %s)", (0, timing))

        # Функция для добавления конца игры
        async def create_end(self):
            timing = datetime.now()
            await self.w(f"INSERT INTO {self.table_name} (start_or_end, timing) VALUES (%s, %s)", (1, timing))

    # Класс для взаимодействия с таблицей Questions_Actions
    class Questions_Actions(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Questions_Actions")

        # Функция для добавления вопроса/действия
        async def create(self, id_admin, questions_or_actions, category, question_action):
            query = f"INSERT INTO {self.table_name} (id_admin, questions_or_actions, category, question_action) VALUES (%s, %s, %s, %s)"
            return await self.w(query, (id_admin, questions_or_actions, category, question_action))

        # Функция для обновления вопроса/действия
        async def update(self, id_admin, id, questions_or_actions, category, question_action):
            query = f"UPDATE {self.table_name} SET id_admin = %s, questions_or_actions = %s, category = %s, question_action = %s WHERE id = %s"
            return await self.w(query, (id_admin, questions_or_actions, category, question_action, id))
        
        # Фунция для взятие количества мин строк по вопросам или действиям, для подсчета кол-ва раундов, которые может провести игра
        async def rounds(self, count_members: int):
            query_false = await self.r(f"SELECT COUNT(*) FROM {self.table_name} WHERE questions_or_actions = false")[0][0]
            query_true = await self.r(f"SELECT COUNT(*) FROM {self.table_name} WHERE questions_or_actions = true")[0][0]
            return int(min(query_false, query_true) / count_members)
        
        # Функция для взятия вопросов и действий
        async def questions_actions(self):
            query_false = await self.r(f"SELECT question_action FROM {self.table_name} WHERE questions_or_actions = false")
            query_true = await self.r(f"SELECT question_action FROM {self.table_name} WHERE questions_or_actions = true")
            
            query_false = [elem[0] for elem in query_false]
            query_true = [elem[0] for elem in query_true]

            return {"question": query_false, "action": query_true}
    
    # Класс для взаимодействия с таблицей Questions_Actions_From_Gamers
    class Questions_Actions_From_Gamers(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Questions_Actions_From_Gamers")

        # Функция для добавления вопроса/действия от игрока
        async def create(self, id_gamer, question_action):
            await self.w(f"INSERT INTO {self.table_name} (id_gamer, question_action) VALUES (%s, %s)", (id_gamer, question_action))

        # Функция для обновления вопроса/действия от игрока
        async def update(self, id, id_gamer, question_action):
            await self.w(f"UPDATE {self.table_name} SET id_gamer = %s, question_action = %s WHERE id = %s", (id_gamer, question_action, id))
    
    # Класс для взаимодействия с таблицей Answers
    class Answers(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Answers")

        # Функция для добавления ответа
        async def create(self, id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score):
            await self.w(
                f"INSERT INTO {self.table_name} (id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                (id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score)
                )

        # Функция для обновления ответа
        async def update(self, id, id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score):
            await self.w(
                f"UPDATE {self.table_name} SET id_game = %s, id_gamer = %s, id_question_action = %s, id_question_action_from_gamer = %s, answer_start = %s, answer_end = %s, score = %s WHERE id = %s", 
                (id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score, id)
                )

    # Класс для взаимодействия с таблицей Participates
    class Participates(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection = None, cursor: mysql.connector.cursor.MySQLCursor = None):
            super().__init__(connection, cursor, "Participates")

        # Функция для добавления подключения участника
        async def create_connection(self, id_game, id_gamer):
            timing = datetime.now()
            await self.w(
                f"INSERT INTO {self.table_name} (id_game, id_gamer, connection_or_disconnection, timing) VALUES (%s, %s, %s, %s)", 
                (id_game, id_gamer, 0, timing)
                )

        # Функция для добавления отключения участника
        async def create_disconnection(self, id_game, id_gamer):
            timing = datetime.now()
            await self.w(
                f"INSERT INTO {self.table_name} (id_game, id_gamer, connection_or_disconnection, timing) VALUES (%s, %s, %s, %s)", 
                (id_game, id_gamer, 1, timing)
                )
        
