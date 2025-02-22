"""| Файл для работы с БД |"""


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.future import select

from datetime import datetime
import logging
import random

# Свои модули
from config.config_reader import config


"""Переменные для работы"""
# Настройка создания подключения к базе
DATABASE_URL = f"mysql+aiomysql://{config.db_user.get_secret_value()}:{config.db_password.get_secret_value()}@{config.db_host.get_secret_value()}/{config.db_name.get_secret_value()}"
engine = create_async_engine(DATABASE_URL, echo= False) # Если echo = True, то он показывает конкретные sql-запросы
Base = declarative_base()
# Переменная, через которую будет производиться подключение к базе
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Настройка логирования
logger = logging.getLogger("sqlalchemy.engine")
logger.propagate = False # удаление дублирования
logger.setLevel(logging.INFO)


"""Классы в виде представления классов SQL"""
class Gamer(Base):
    __tablename__ = "Gamers"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Внутренние
    username = Column(String(63), index=True)

class Admin(Base):
    __tablename__ = "Admins"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Внутренние
    username = Column(String(63), index=True)

class Chat(Base):
    __tablename__ = "Chats"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Внутренние
    name = Column(String)
    type = Column(Enum("private", "group", "supergroup", "channel"), nullable= False)
    num_members = Column(Integer)
    bot_is_kicked = Column(Boolean, default= False)

class Game(Base):
    __tablename__ = "Games"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Сторонние
    id_chat = Column(Integer, ForeignKey("Chats.id"))
    # Внутренние
    rounds = Column(Integer)
    finished_at= Column(DateTime, nullable=True) 

    chat = relationship("Chat")

class Participant(Base):
    __tablename__ = "Participants"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Сторонние
    id_game = Column(Integer, ForeignKey('Games.id'))
    id_gamer = Column(Integer, ForeignKey('Gamers.id'))
    # Внутренние 
    score = Column(Integer, default= 0)

    game = relationship("Game")
    gamer = relationship("Gamer")

class QuestionAction(Base):
    __tablename__ = "Questions_Actions"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Сторонние
    id_admin = Column(Integer, ForeignKey('Admins.id', ondelete= "SET NULL"))
    # Внутренние
    question_or_action = Column(Boolean)
    category = Column(Enum("Активность", "Философия", "Гипотетические ситуации", "Мечты и страхи", "Прошлое", "Юмор", "Пошлое", "Кринж"), nullable = False)
    question_action = Column(String, unique=True)

    admin = relationship("Admin")

class QuestionActionFromGamer(Base):
    __tablename__ = "Questions_Actions_From_Gamers"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Сторонние
    id_gamer = Column(Integer, ForeignKey('Gamers.id'))
    # Внутренние
    question_action = Column(String)

    gamer = relationship("Gamer")

class Answer(Base):
    __tablename__ = "Answers"
    # Базовые
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    # Сторонние
    id_paricipant = Column(Integer, ForeignKey('Participants.id'))
    id_question_action = Column(Integer, ForeignKey('Questions_Actions.id', ondelete= "SET NULL"), nullable=True)
    id_question_action_from_gamer = Column(Integer, ForeignKey('Questions_Actions_From_Gamers.id', ondelete= "SET NULL"), nullable=True)
    # Внутренние
    round = Column(Integer)
    finished_at = Column(DateTime, nullable= True)
    score = Column(Integer, nullable= True)

    participant = relationship("Participant")
    question_action = relationship("QuestionAction", foreign_keys=[id_question_action])
    question_action_from_gamer = relationship("QuestionActionFromGamer", foreign_keys=[id_question_action_from_gamer])



"""Главный класс для взаимодействия с базой"""
class DataBase:
    class __Base:
        def __init__(self, session, model):
            self.session = session
            self.model = model

        async def create(self, **kwargs):
            try:
                async with self.session as session:
                    async with session.begin():
                        # Автоматически заполняем created_at, если его нет в таблице и оно не указано (так то это поле есть во всех таблицах, просто вдруг оно будет убрано когда-нибудь)
                        if 'created_at' in self.model.__table__.columns and 'created_at' not in kwargs:
                            kwargs['created_at'] = datetime.now()

                        instance = self.model(**kwargs)
                        session.add(instance)
                    await session.commit()
                    return instance
            except Exception as ex:
                logger.error(f"Ошибка создания записи в таблице {self.model.__tablename__}: {ex}")
                return None

        async def read(self, id):
            try:
                async with self.session as session:
                    result = await session.execute(select(self.model).where(self.model.id == id))
                    return result.scalars().first()
            except Exception as ex:
                logger.error(f"Ошибка чтения записи из таблицы {self.model.__tablename__}: {ex}")
                return None

        async def read_all(self):
            try:
                async with self.session as session:
                    result = await session.execute(select(self.model))
                    return result.scalars().all()
            except Exception as ex:
                logger.error(f"Ошибка чтения всех записей из таблицы {self.model.__tablename__}: {ex}")
                return []

        async def read_by_page(self, page: int, limit: int = 5):
            try:
                async with self.session as session:
                    # Вычисляем количество элементов, которые нужно пропустить
                    offset_value = page * limit
                    result = await session.execute(
                        select(self.model)
                        .order_by(self.model.created_at.desc())  # Сортировка по дате создания
                        .offset(offset_value)  # Пропустить предыдущие элементы
                        .limit(limit)  # Ограничение на 5 элементов
                    )
                    return result.scalars().all()  # Возвращаем список элементов
            except Exception as ex:
                logger.error(f"Ошибка при чтении записей с разбивкой по страницам из таблицы {self.model.__tablename__}: {ex}")
                return []


        async def update(self, id, **kwargs):
            try:
                async with self.session as session:
                    async with session.begin():
                        result = await session.execute(select(self.model).where(self.model.id == id))
                        instance = result.scalars().first()
                        if instance:
                            # Обновление существующего объекта
                            for key, value in kwargs.items():
                                setattr(instance, key, value)
                            session.add(instance)
                        else:
                            logger.error(f"Запись с id={id} не найдена.")
                            return None
                        
                    await session.commit()
                    return instance
            except Exception as ex:
                logger.error(f"Ошибка обновления записи в таблице {self.model.__tablename__}: {ex}")
                return None

        async def delete(self, id):
            try:
                async with self.session as session:
                    async with session.begin():
                        result = await session.execute(select(self.model).where(self.model.id == id))
                        instance = result.scalars().first()
                        if instance:
                            await session.delete(instance)
                            await session.commit()
                            return instance
                        else:
                            await session.rollback()
                            return None
            except Exception as ex:
                logger.error(f"Ошибка удаления записи из таблицы {self.model.__tablename__}: {ex}")
                return None
        
        # Метод проверки, есть ли запись с таким id в таблице
        async def is_exists(self, id):
            try:
                async with self.session as session:
                    result = await session.execute(select(self.model).where(self.model.id == id))
                    return result.scalars().first() is not None
            except Exception as ex:
                logger.error(f"Ошибка проверки наличия записи в таблице {self.model.__tablename__}: {ex}")
                return False
        
        # Метод выдачи id первого элемента таблицы
        async def oldest_id(self):
            try:
                async with self.session as session:
                    result = await session.execute(
                        select(self.model.id).order_by(self.model.created_at.asc()).limit(1)
                    )
                    first_id = result.scalar()
                    return first_id
            except Exception as ex:
                logger.error(f"Ошибка получения первого id из таблицы {self.model.__tablename__}: {ex}")
                return None

        # Метод выдачи конечного существующего id в таблицеы
        async def newest_id(self):
            try:
                async with self.session as session:
                    result = await session.execute(
                        select(self.model.id).order_by(self.model.created_at.desc()).limit(1)
                    )
                    last_id = result.scalar()
                    return last_id
            except Exception as ex:
                logger.error(f"Ошибка получения последнего id по времени создания в таблице {self.model.__tablename__}: {ex}")
                return None

        
        # Метод, который выдеает количество элементов в таблице
        async def length(self):
            try:
                async with self.session as session:
                    result = await session.execute(
                        select(func.count()).select_from(self.model)
                    )
                    count = result.scalar()
                    return count
            except Exception as ex:
                logger.error(f"Ошибка получения количества записей в таблице {self.model.__tablename__}: {ex}")
                return 0


    class Gamers(__Base):
        def __init__(self, session):
            super().__init__(session, Gamer)

    class Admins(__Base):
        def __init__(self, session):
            super().__init__(session, Admin)

    class Chats(__Base):
        def __init__(self, session):
            super().__init__(session, Chat) 

    class Games(__Base):
        def __init__(self, session):
            super().__init__(session, Game)

        async def finish(self, id_game: int):
            try: 
                return await self.update(id= id_game, finished_at= datetime.now())
            except Exception as ex:
                logger.error(f"Ошибка добавления финиша игры с id= {id_game}: {ex}")
                return None


    class Questions_Actions(__Base):
        def __init__(self, session):
            super().__init__(session, QuestionAction)

        async def count_max_rounds(self, count_members: int):
            try:
                async with self.session as session:
                    result_false = await session.execute(select(self.model).where(self.model.question_or_action == False))
                    count_questions = len(result_false.scalars().all())
                    result_true = await session.execute(select(self.model).where(self.model.question_or_action == True))
                    count_actions = len(result_true.scalars().all())
                    return int(min(count_questions, count_actions) / count_members)
            except Exception as ex:
                logger.error(f"Ошибка расчета количества раундов в таблице {self.model.__tablename__}: {ex}")
                return 0


        async def make_rounds(self, num_rounds: int, num_participants: int):
            try:
                async with self.session as session:
                    result_false = await session.execute(select(self.model).where(self.model.question_or_action == False))
                    questions = [elem for elem in result_false.scalars().all()]
                    questions = random.sample(questions, num_rounds*num_participants)

                    result_true = await session.execute(select(self.model).where(self.model.question_or_action == True))
                    actions = [elem for elem in result_true.scalars().all()]
                    actions = random.sample(actions, num_rounds*num_participants)

                    return {False: questions, True: actions}
            except Exception as ex:
                logger.error(f"Ошибка получения вопросов и действий из таблицы {self.model.__tablename__}: {ex}")
                return None

    class Questions_Actions_From_Gamers(__Base):
        def __init__(self, session):
            super().__init__(session, QuestionActionFromGamer)

    class Answers(__Base):
        def __init__(self, session):
            super().__init__(session, Answer)

        async def finish(self, id_answer):
            """Добавляет конец (end_time) в запись с указанным id"""
            try:
                return await self.update(id_answer, finished_at= datetime.now())
            except Exception as ex:
                logger.error(f"Ошибка добавления времени завершения ответа с id={id_answer}: {ex}")
                return None

        async def add_score(self, id_answer, score):
            """Добавляет результат (score) в запись с указанным id"""
            try:
                return await self.update(id_answer, score=score)
            except Exception as ex:
                logger.error(f"Ошибка добавления результата ответа с id={id_answer}: {ex}")
                return None


    class Participants(__Base):
        def __init__(self, session):
            super().__init__(session, Participant)


"""Пример использования базы данных"""
if __name__ == "__main__":
    import asyncio

    async def example_usage():
        async with async_session() as session:
            gamers_db = DataBase.Gamers(session)
            # Добавление записи
            await gamers_db.create(id= 12345, username= 'example_user')
            exists = await gamers_db.is_exists(12345)
            print(f"Gamer exists: {exists}")

            # Чтение всех записей
            all_gamers = await gamers_db.read_all()
            print("All gamers:")
            for gamer in all_gamers:
                print(f"ID: {gamer.id}, Username: {gamer.username}")
            
            # Получение списка колонок в таблице
            attributes = [column.name for column in gamers_db.model.__table__.columns]
            response = '\n'.join([
                "ID: %s, Username: %s" % tuple(getattr(gamer, attr) for attr in attributes)
                for gamer in all_gamers
            ])
            print(response)

            # Удаление записи
            await gamers_db.delete(id=12345)
            exists = await gamers_db.is_exists(12345)
            print(f"Gamer exists: {exists}")

            

    asyncio.run(example_usage())
