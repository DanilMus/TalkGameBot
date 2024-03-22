import mysql.connector
from config import config

class DataBase():
    def __init__(self):
        # Создаем соединение с базой данных
        self.connection = mysql.connector.connect(user= config.db_user, 
                                                password= config.db_password,
                                                host= config.db_host,
                                                database=config.db_name)
        
        self.admins = self.Admins(self.connection)
        self.questions_actions = self.Questions_Actions(self.connection)

    
    class Admins():
        def __init__(self, connection: mysql.connector.MySQLConnection):
            self.connection = connection
            self.cursor = connection.cursor()
            self.table_name = "Admins"

        # Функция для добавления админа
        def create(self, id, nickname):
            query = f"INSERT INTO {self.table_name} (id, nickname) VALUES (%s, %s)"
            self.cursor.execute(query, (id, nickname))
            self.connection.commit()
        
        # Функция для чтения всех админов
        def read(self):
            query = f"SELECT * FROM {self.table_name}"
            self.cursor.execute(query)
            result = self.cursor.fetchall()

            return result

        # Функция для обновления информации об админе
        def update(self, id, nickname):
            query = f"UPDATE {self.table_name} SET nickname = %s WHERE id = %s"
            self.cursor.execute(query, (nickname, id))
            self.connection.commit()

        # Функция для удаления админа
        def delete(self, id):
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            self.cursor.execute(query, (id,))
            self.connection.commit()
        
        # Функция для удаления всех админов
        def delete_all(self):
            query = f"DELETE FROM {self.table_name}"
            self.cursor.execute(query)
            self.connection.commit()

    class Questions_Actions():
        def __init__(self, connection: mysql.connector.MySQLConnection):
            self.connection = connection
            self.cursor = connection.cursor()
            self.table_name = "Questions_Actions"

        # Метод для проверки существования в таблице
        def is_admin(self, id):
            query = f"SELECT * FROM Admins WHERE id = %s"
            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            return result is not None

        # Функция для добавления вопроса/действия
        def create(self, id_admin, questions_or_actions, category, task):
            if not self.is_admin(id_admin):
                raise Exception("Access denied. The user is not an admin.")
            
            query = f"INSERT INTO {self.table_name} (id_admin, questions_or_actions, category, task) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (id_admin, questions_or_actions, category, task))
            self.connection.commit()

        # Функция для чтения всех вопросов/действий
        def read(self, id_admin):
            if not self.is_admin(id_admin):
                raise Exception("Access denied. The user is not an admin.")

            query = f"SELECT * FROM {self.table_name}"
            self.cursor.execute(query)
            result = self.cursor.fetchall()

            return result

        # Функция для обновления вопроса/действия
        def update(self, id_admin, id, questions_or_actions, category, task):
            if not self.is_admin(id_admin):
                raise Exception("Access denied. The user is not an admin.")
            
            query = f"UPDATE {self.table_name} SET id_admin = %s, questions_or_actions = %s, category = %s, task = %s WHERE id = %s"
            self.cursor.execute(query, (id_admin, questions_or_actions, category, task, id))
            self.connection.commit()

        # Функция для удаления вопроса/действия
        def delete(self, id_admin, id):
            if not self.is_admin(id_admin):
                raise Exception("Access denied. The user is not an admin.")
            
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            self.cursor.execute(query, (id,))
            self.connection.commit()

        # Функция для удаления всех вопросов/действий
        def delete_all(self, id_admin):
            if not self.is_admin(id_admin):
                raise Exception("Access denied. The user is not an admin.")

            query = f"DELETE FROM {self.table_name}"
            self.cursor.execute(query)
            self.connection.commit()

