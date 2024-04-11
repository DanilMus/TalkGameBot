import mysql.connector
from config import bot_config

class DataBase():
    def __init__(self):
        # Создаем соединение с базой данных
        self.connection = mysql.connector.connect(user= bot_config.db_user, 
                                                password= bot_config.db_password,
                                                host= bot_config.db_host,
                                                database=bot_config.db_name)
        
        self.admins = self.Admins(self.connection)
        self.questions_actions = self.Questions_Actions(self.connection, self.admins)
    
    def close(self):
        self.connection.close()

    
    class Admins():
        def __init__(self, connection: mysql.connector.MySQLConnection):
            self.connection = connection
            self.cursor = connection.cursor()
            self.table_name = "Admins"

        # Для чтения
        def r(self, query: str, id_admin: int, data = ()):
            try: 
                if id_admin != bot_config.creator:
                    raise Exception("Доступ запрещен. Пользователь не является главным админом.")

                self.cursor.execute(query, data)
                return self.cursor.fetchone() is not None
            except mysql.connector.Error as err:
                print(f"Проблема с подключением к базе: {err}")
                return None
        
        # Для записи
        def w(self, query: str, id_admin: int, data = ()):
            try:
                if id_admin != bot_config.creator:
                    raise Exception("Доступ запрещен. Пользователь не является главным админом.")

                self.cursor.execute(query, data)
                self.connection.commit()
            except mysql.connector.Error as err:
                print(f"Проблема с подключением к базе: {err}")
        

        # Метод для проверки существования в таблице
        def is_admin(self, id):
            try: 
                query = (f"SELECT * FROM {self.table_name} WHERE id = %s")
                data = (id, )
                self.cursor.execute(query, data)
                return self.cursor.fetchone() is not None
            except mysql.connector.Error as err:
                print(f"Проблема с подключением к базе: {err}")
                return None

        # Функция для добавления админа
        def create(self, id_admin, id, nickname):
            self.w(f"INSERT INTO {self.table_name} (id, nickname) VALUES (%s, %s)", id_admin, (id, nickname))
        
        # Функция для чтения всех админов
        def read(self, id_admin):
            return self.r(f"SELECT * FROM {self.table_name}", id_admin)

        # Функция для обновления информации об админе
        def update(self, id_admin, id, nickname):
            self.w(f"UPDATE {self.table_name} SET nickname = %s WHERE id = %s", id_admin, (nickname, id))

        # Функция для удаления админа
        def delete(self, id_admin, id):
            self.w(f"DELETE FROM {self.table_name} WHERE id = %s", id_admin, (id,))
        
        # Функция для удаления всех админов
        def delete_all(self, id_admin):
            self.w(f"DELETE FROM {self.table_name}", id_admin)


    class Questions_Actions():
        def __init__(self, connection: mysql.connector.MySQLConnection, admins):
            self.connection = connection
            self.cursor = connection.cursor()
            self.table_name = "Questions_Actions"
            self.admins = admins

        # Для чтения
        def r(self, query: str, id_admin: int, data = ()):
            try:
                if not self.admins.is_admin(id_admin):
                    raise Exception("Доступ запрещен. Пользователь не является админом.")
                
                self.cursor.execute(query, data)
                return self.cursor.fetchone() is not None
            except mysql.connector.Error as err:
                print(f"Проблема с подключением к базе: {err}")
                return None
            except Exception as ex:
                print(f"Что-то пошло не так: {ex}")
                return None
        
        # Для записи
        def w(self, query: str, id_admin: int, data = ()):
            try:
                if not self.admins.is_admin(id_admin):
                    raise Exception("Доступ запрещен. Пользователь не является админом.")

                self.cursor.execute(query, data)
                self.connection.commit()
            except mysql.connector.Error as err:
                print(f"Проблема с подключением к базе: {err}")
                return None
            except Exception as ex:
                print(f"Что-то пошло не так: {ex}")
                return None


        # Функция для добавления вопроса/действия
        def create(self, id_admin, questions_or_actions, category, task):
            query = f"INSERT INTO {self.table_name} (id_admin, questions_or_actions, category, task) VALUES (%s, %s, %s, %s)"
            self.w(query, id_admin, (id_admin, questions_or_actions, category, task))

        # Функция для чтения всех вопросов/действий
        def read(self, id_admin):
            return self.r(f"SELECT * FROM {self.table_name}", id_admin)

        # Функция для обновления вопроса/действия
        def update(self, id_admin, id, questions_or_actions, category, task):
            query = f"UPDATE {self.table_name} SET id_admin = %s, questions_or_actions = %s, category = %s, task = %s WHERE id = %s"
            self.w(query, id_admin, (id_admin, questions_or_actions, category, task, id))

        # Функция для удаления вопроса/действия
        def delete(self, id_admin, id):
            self.w(f"DELETE FROM {self.table_name} WHERE id = %s", id_admin, (id,))

        # Функция для удаления всех вопросов/действий
        def delete_all(self, id_admin):
            self.w(f"DELETE FROM {self.table_name}", id_admin)