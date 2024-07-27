from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.future import select
from datetime import datetime
import logging
from config import config

DATABASE_URL = f"mysql+aiomysql://{config.db_user}:{config.db_password}@{config.db_host}/{config.db_name}"

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

logger = logging.getLogger(__name__)

class Gamer(Base):
    __tablename__ = "Gamers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(63), index=True)

class Admin(Base):
    __tablename__ = "Admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(63), index=True)

class Game(Base):
    __tablename__ = "Games"
    id = Column(Integer, primary_key=True, index=True)
    start_or_end = Column(Boolean)
    timing = Column(DateTime)

class QuestionAction(Base):
    __tablename__ = "Questions_Actions"
    id = Column(Integer, primary_key=True, index=True)
    id_admin = Column(Integer, ForeignKey('Admins.id'))
    questions_or_actions = Column(Boolean)
    category = Column(String(127))
    question_action = Column(String, unique=True)
    admin = relationship("Admin")

class QuestionActionFromGamer(Base):
    __tablename__ = "Questions_Actions_From_Gamers"
    id = Column(Integer, primary_key=True, index=True)
    id_gamer = Column(Integer, ForeignKey('Gamers.id'))
    question_action = Column(String)
    gamer = relationship("Gamer")

class Answer(Base):
    __tablename__ = "Answers"
    id = Column(Integer, primary_key=True, index=True)
    id_game = Column(Integer, ForeignKey('Games.id'))
    id_gamer = Column(Integer, ForeignKey('Gamers.id'))
    id_question_action = Column(Integer, ForeignKey('Questions_Actions.id'), nullable=True)
    id_question_action_from_gamer = Column(Integer, ForeignKey('Questions_Actions_From_Gamers.id'), nullable=True)
    answer_start = Column(DateTime)
    answer_end = Column(DateTime)
    score = Column(Integer)
    game = relationship("Game")
    gamer = relationship("Gamer")
    question_action = relationship("QuestionAction", foreign_keys=[id_question_action])
    question_action_from_gamer = relationship("QuestionActionFromGamer", foreign_keys=[id_question_action_from_gamer])

class Participate(Base):
    __tablename__ = "Participates"
    id = Column(Integer, primary_key=True, index=True)
    id_game = Column(Integer, ForeignKey('Games.id'))
    id_gamer = Column(Integer, ForeignKey('Gamers.id'))
    connection_or_disconnection = Column(Boolean)
    timing = Column(DateTime)
    game = relationship("Game")
    gamer = relationship("Gamer")

class DataBase:
    class __Base:
        def __init__(self, session, model):
            self.session = session
            self.model = model

        async def create(self, **kwargs):
            try:
                async with self.session as session:
                    async with session.begin():
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

        async def update(self, id, **kwargs):
            try:
                async with self.session as session:
                    async with session.begin():
                        result = await session.execute(select(self.model).where(self.model.id == id))
                        instance = result.scalars().first()
                        if instance:
                            for key, value in kwargs.items():
                                setattr(instance, key, value)
                            session.add(instance)
                        else:
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
            
        async def is_exists(self, id):
            try:
                async with self.session as session:
                    result = await session.execute(select(self.model).where(self.model.id == id))
                    return result.scalars().first() is not None
            except Exception as ex:
                logger.error(f"Ошибка проверки наличия записи в таблице {self.model.__tablename__}: {ex}")
                return False

    class Gamers(__Base):
        def __init__(self, session):
            super().__init__(session, Gamer)

    class Admins(__Base):
        def __init__(self, session):
            super().__init__(session, Admin)

    class Games(__Base):
        def __init__(self, session):
            super().__init__(session, Game)

        async def create_start(self):
            return await self.create(start_or_end=False, timing=datetime.now())

        async def create_end(self):
            return await self.create(start_or_end=True, timing=datetime.now())

    class Questions_Actions(__Base):
        def __init__(self, session):
            super().__init__(session, QuestionAction)

        async def rounds(self, count_members: int):
            try:
                async with self.session as session:
                    result_false = await session.execute(select(self.model).where(self.model.questions_or_actions == False))
                    count_false = result_false.scalars().count()
                    result_true = await session.execute(select(self.model).where(self.model.questions_or_actions == True))
                    count_true = result_true.scalars().count()
                    return int(min(count_false, count_true) / count_members)
            except Exception as ex:
                logger.error(f"Ошибка расчета количества раундов в таблице {self.model.__tablename__}: {ex}")
                return 0

        async def questions_actions(self):
            try:
                async with self.session() as session:
                    result_false = await session.execute(select(self.model).where(self.model.questions_or_actions == False))
                    questions = [elem.question_action for elem in result_false.scalars().all()]
                    result_true = await session.execute(select(self.model).where(self.model.questions_or_actions == True))
                    actions = [elem.question_action for elem in result_true.scalars().all()]
                    return {"question": questions, "action": actions}
            except Exception as ex:
                logger.error(f"Ошибка получения вопросов и действий из таблицы {self.model.__tablename__}: {ex}")
                return {"question": [], "action": []}

    class Questions_Actions_From_Gamers(__Base):
        def __init__(self, session):
            super().__init__(session, QuestionActionFromGamer)

    class Answers(__Base):
        def __init__(self, session):
            super().__init__(session, Answer)

    class Participates(__Base):
        def __init__(self, session):
            super().__init__(session, Participate)

        async def create_connection(self, id_game, id_gamer):
            return await self.create(id_game=id_game, id_gamer=id_gamer, connection_or_disconnection=False, timing=datetime.now())

        async def create_disconnection(self, id_game, id_gamer):
            return await self.create(id_game=id_game, id_gamer=id_gamer, connection_or_disconnection=True, timing=datetime.now())


# Пример использования базы данных
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
            
            # Удаление записи
            await gamers_db.delete(id=12345)
            exists = await gamers_db.is_exists(12345)
            print(f"Gamer exists: {exists}")

    asyncio.run(example_usage())
