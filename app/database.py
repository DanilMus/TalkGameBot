# 
# Взаимодействие с БД
# 

# Библиотеки
import mysql.connector
import mysql.connector.cursor
import logging
from abc import ABC # Для создания абстрактных классов

# Свои модули
from config import bot_config


logger = logging.getLogger(__name__) # логирование событий
# Класс для взаимодействия с базой
class DataBase():
    def __init__(self):
        # Создаем соединение с базой данных
        self.connection = mysql.connector.connect(user= bot_config.db_user, 
                                                password= bot_config.db_password,
                                                host= bot_config.db_host,
                                                database=bot_config.db_name,
                                                charset= "utf8")
        self.cursor = self.connection.cursor()
        
        self.gamers = self._Gamers(self.connection, self.cursor)
        self.admins = self._Admins(self.connection, self.cursor)
        self.games = self._Games(self.connection, self.cursor)
        self.questions_actions = self._Questions_Actions(self.connection, self.cursor)
        self.questions_actions_from_gamers = self._Questions_Actions_From_Gamers(self.connection, self.cursor)
        self.answers = self._Answers(self.connection, self.cursor)
        self.participates = self._Participates(self.connection, self.cursor)
    
    # Закрытие соединения
    def close(self):
        self.connection.close()
    
    # Восстановление соединения
    def connect(self):
        self.connection = mysql.connector.connect(user= bot_config.db_user, 
                                                password= bot_config.db_password,
                                                host= bot_config.db_host,
                                                database=bot_config.db_name,
                                                charset= "utf8")
        self.cursor = self.connection.cursor()
    

    # База для взаимодействиями с таблицами
    class __Base(ABC):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor, table_name: str):
            self.connection = connection
            self.cursor = cursor
            self.table_name = table_name


        # Для чтения
        def r(self, query: str, data = ()):
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
        def w(self, query: str, data = ()):
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
        def read(self):
            return self.r(f"SELECT * FROM {self.table_name}")
        
        # Функция для удаления (она тоже у всех одинаковая)
        def delete(self, id):
            self.w(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))

    # База для взаимодействия с таблицами Gamers, Admins
    class __PeopleBase(__Base, ABC):
        # Метод для проверки существования в таблице
        def is_exists(self, id):
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
        def create(self, id, nickname):
            return self.w(f"INSERT INTO {self.table_name} (id, nickname) VALUES (%s, %s)", (id, nickname))

        # Функция для обновления информации об человеке
        def update(self, id, nickname):
            return self.w(f"UPDATE {self.table_name} SET nickname = %s WHERE id = %s", (nickname, id))


    # Класс для взаимодействия с таблицей Gamers
    class _Gamers(__PeopleBase):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Gamers")


    # Класс для взаимодействия с таблицей Admins
    class _Admins(__PeopleBase):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Admins")


    # Класс для взаимодействия с таблицей Games
    class _Games(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Games")
        
        # Функция для добавления игры
        def create(self, game_start, game_end):
            self.w(f"INSERT INTO {self.table_name} (game_start, game_end) VALUES (%s, %s)", (game_start, game_end))

        # Функция для обновления информации об игре
        def update(self, id, game_start, game_end):
            self.w(f"UPDATE {self.table_name} SET game_start = %s, game_end = %s WHERE id = %s", (game_start, game_end, id))



    # Класс для взаимодействия с таблицей Questions_Actions
    class _Questions_Actions(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Questions_Actions")

        # Функция для добавления вопроса/действия
        def create(self, id_admin, questions_or_actions, category, task):
            query = f"INSERT INTO {self.table_name} (id_admin, questions_or_actions, category, task) VALUES (%s, %s, %s, %s)"
            return self.w(query, (id_admin, questions_or_actions, category, task))

        # Функция для обновления вопроса/действия
        def update(self, id_admin, id, questions_or_actions, category, task):
            query = f"UPDATE {self.table_name} SET id_admin = %s, questions_or_actions = %s, category = %s, task = %s WHERE id = %s"
            return self.w(query, (id_admin, questions_or_actions, category, task, id))
        
    
    # Класс для взаимодействия с таблицей Questions_Actions_From_Gamers
    class _Questions_Actions_From_Gamers(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Questions_Actions_From_Gamers")

        # Функция для добавления вопроса/действия от игрока
        def create(self, id_gamer, task):
            self.w(f"INSERT INTO {self.table_name} (id_gamer, task) VALUES (%s, %s)", (id_gamer, task))

        # Функция для обновления вопроса/действия от игрока
        def update(self, id, id_gamer, task):
            self.w(f"UPDATE {self.table_name} SET id_gamer = %s, task = %s WHERE id = %s", (id_gamer, task, id))
    
    # Класс для взаимодействия с таблицей Answers
    class _Answers(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Answers")

        # Функция для добавления ответа
        def create(self, id_game, id_gamer, id_question_action, id_question_action_from_gamer, from_game_or_gamer, answer_start, answer_end, score):
            self.w(
                f"INSERT INTO {self.table_name} (id_game, id_gamer, id_question_action, id_question_action_from_gamer, from_game_or_gamer, answer_start, answer_end, score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                (id_game, id_gamer, id_question_action, id_question_action_from_gamer, from_game_or_gamer, answer_start, answer_end, score)
                )

        # Функция для обновления ответа
        def update(self, id, id_game, id_gamer, id_question_action, id_question_action_from_gamer, from_game_or_gamer, answer_start, answer_end, score):
            self.w(
                f"UPDATE {self.table_name} SET id_game = %s, id_gamer = %s, id_question_action = %s, id_question_action_from_gamer = %s, from_game_or_gamer = %s, answer_start = %s, answer_end = %s, score = %s WHERE id = %s", 
                (id_game, id_gamer, id_question_action, id_question_action_from_gamer, from_game_or_gamer, answer_start, answer_end, score, id)
                )
        
    # Класс для взаимодействия с таблицей Participates
    class _Participates(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Participates")

        # Функция для добавления участника
        def create(self, id_game, id_gamer, connection_time, disconnection_time):
            self.w(
                f"INSERT INTO {self.table_name} (id_game, id_gamer, connection_time, disconnection_time) VALUES (%s, %s, %s, %s)", 
                (id_game, id_gamer, connection_time, disconnection_time)
                )

        # Функция для обновления информации об участнике
        def update(self, id, id_game, id_gamer, connection_time, disconnection_time):
            self.w(
                f"UPDATE {self.table_name} SET id_game = %s, id_gamer = %s, connection_time = %s, disconnection_time = %s WHERE id = %s", 
                (id_game, id_gamer, connection_time, disconnection_time, id)
                )
        
    
        

db = DataBase() # экземпляр класса для взаимодействия