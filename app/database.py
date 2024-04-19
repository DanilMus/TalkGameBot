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


# Класс для взаимодействия с базой
logger = logging.getLogger(__name__) # логирование событий
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
        self.questions_actions = self._Questions_Actions(self.connection, self.cursor)
    
    def close(self):
        self.connection.close()
    
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

        # Функция для добавления админа
        def create(self, id, nickname):
            return self.w(f"INSERT INTO {self.table_name} (id, nickname) VALUES (%s, %s)", (id, nickname))
        
        # Функция для чтения всех админов
        def read(self):
            return self.r(f"SELECT * FROM {self.table_name}")

        # Функция для обновления информации об админе
        def update(self, id, nickname):
            return self.w(f"UPDATE {self.table_name} SET nickname = %s WHERE id = %s", (nickname, id))

        # Функция для удаления админа
        def delete(self, id):
            return self.w(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))
        
        # Функция для удаления всех админов
        def delete_all(self):
            return self.w(f"DELETE FROM {self.table_name}")

    # Класс для взаимодействия с таблицей Gamers
    class _Gamers(__PeopleBase):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Gamers")
            
    # Класс для взаимодействия с таблицей Admins
    class _Admins(__PeopleBase):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Admins")

    # Класс для взаимодействия с таблицей Questions_Actions
    class _Questions_Actions(__Base):
        def __init__(self, connection: mysql.connector.MySQLConnection, cursor: mysql.connector.cursor.MySQLCursor):
            super().__init__(connection, cursor, "Questions_Actions")

        # Функция для добавления вопроса/действия
        def create(self, id_admin, questions_or_actions, category, task):
            query = f"INSERT INTO {self.table_name} (id_admin, questions_or_actions, category, task) VALUES (%s, %s, %s, %s)"
            return self.w(query, (id_admin, questions_or_actions, category, task))

        # Функция для чтения всех вопросов/действий
        def read(self):
            return self.r(f"SELECT * FROM {self.table_name}")

        # Функция для обновления вопроса/действия
        def update(self, id_admin, id, questions_or_actions, category, task):
            query = f"UPDATE {self.table_name} SET id_admin = %s, questions_or_actions = %s, category = %s, task = %s WHERE id = %s"
            return self.w(query, (id_admin, questions_or_actions, category, task, id))

        # Функция для удаления вопроса/действия
        def delete(self, id):
            return self.w(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))

        # Функция для удаления всех вопросов/действий
        def delete_all(self):
            return self.w(f"DELETE FROM {self.table_name}")
        
    
        

db = DataBase() # экземпляр класса для взаимодействия