# Взаимодействие с БД через SQLAlchemy

# Библиотеки
from sqlalchemy import create_engine, Column, String, Integer, BigInteger, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from abc import ABC
from datetime import datetime
import logging
from config import config

logger = logging.getLogger(__name__)

# Настройка подключения к базе данных
DATABASE_URL = f"mysql+mysqlconnector://{config.db_user}:{config.db_password}@{config.db_host}/{config.db_name}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Модели таблиц
class Gamer(Base):
    __tablename__ = 'Gamers'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(63))

class Admin(Base):
    __tablename__ = 'Admins'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(63))

class Game(Base):
    __tablename__ = 'Games'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_or_end = Column(Boolean)
    timing = Column(DateTime)

class QuestionAction(Base):
    __tablename__ = 'Questions_Actions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_admin = Column(BigInteger, ForeignKey('Admins.id'))
    questions_or_actions = Column(Boolean)
    category = Column(String(127))
    question_action = Column(Text, unique=True)
    admin = relationship("Admin")

class QuestionActionFromGamer(Base):
    __tablename__ = 'Questions_Actions_From_Gamers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_gamer = Column(BigInteger, ForeignKey('Gamers.id'))
    question_action = Column(Text)
    gamer = relationship("Gamer")

class Answer(Base):
    __tablename__ = 'Answers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_game = Column(Integer, ForeignKey('Games.id'))
    id_gamer = Column(BigInteger, ForeignKey('Gamers.id'))
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
    __tablename__ = 'Participates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_game = Column(Integer, ForeignKey('Games.id'))
    id_gamer = Column(BigInteger, ForeignKey('Gamers.id'))
    connection_or_disconnection = Column(Boolean)
    timing = Column(DateTime)
    game = relationship("Game")
    gamer = relationship("Gamer")

# Создание таблиц
Base.metadata.create_all(engine)

# Класс для взаимодействия с базой данных
class DataBase:
    class __Base(ABC):
        def __init__(self, session, model):
            self.session = session
            self.model = model

        async def read(self):
            return self.session.query(self.model).all()

        async def delete(self, id):
            try:
                obj = self.session.query(self.model).filter_by(id=id).first()
                if obj:
                    self.session.delete(obj)
                    self.session.commit()
                    return True
                return False
            except Exception as ex:
                logger.error(f"Error deleting from {self.model.__tablename__}: {ex}")
                return False

    class __PeopleBase(__Base, ABC):
        async def is_exists(self, id):
            try:
                return self.session.query(self.model).filter_by(id=id).first() is not None
            except Exception as ex:
                logger.error(f"Error checking existence in {self.model.__tablename__}: {ex}")
                return False

        async def create(self, id, username):
            try:
                new_person = self.model(id=id, username=username)
                self.session.add(new_person)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating in {self.model.__tablename__}: {ex}")
                return False

        async def update(self, id, username):
            try:
                person = self.session.query(self.model).filter_by(id=id).first()
                if person:
                    person.username = username
                    self.session.commit()
                    return True
                return False
            except Exception as ex:
                logger.error(f"Error updating in {self.model.__tablename__}: {ex}")
                return False

    class Gamers(__PeopleBase):
        def __init__(self, session):
            super().__init__(session, Gamer)

    class Admins(__PeopleBase):
        def __init__(self, session):
            super().__init__(session, Admin)

    class Games(__Base):
        def __init__(self, session):
            super().__init__(session, Game)

        async def create_start(self):
            try:
                new_game = self.model(start_or_end=False, timing=datetime.now())
                self.session.add(new_game)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating start game in {self.model.__tablename__}: {ex}")
                return False

        async def create_end(self):
            try:
                new_game = self.model(start_or_end=True, timing=datetime.now())
                self.session.add(new_game)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating end game in {self.model.__tablename__}: {ex}")
                return False

    class Questions_Actions(__Base):
        def __init__(self, session):
            super().__init__(session, QuestionAction)

        async def create(self, id_admin, questions_or_actions, category, question_action):
            try:
                new_qa = self.model(id_admin=id_admin, questions_or_actions=questions_or_actions, category=category, question_action=question_action)
                self.session.add(new_qa)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating in {self.model.__tablename__}: {ex}")
                return False

        async def update(self, id, id_admin, questions_or_actions, category, question_action):
            try:
                qa = self.session.query(self.model).filter_by(id=id).first()
                if qa:
                    qa.id_admin = id_admin
                    qa.questions_or_actions = questions_or_actions
                    qa.category = category
                    qa.question_action = question_action
                    self.session.commit()
                    return True
                return False
            except Exception as ex:
                logger.error(f"Error updating in {self.model.__tablename__}: {ex}")
                return False

        async def rounds(self, count_members):
            try:
                query_false = self.session.query(self.model).filter_by(questions_or_actions=False).count()
                query_true = self.session.query(self.model).filter_by(questions_or_actions=True).count()
                return int(min(query_false, query_true) / count_members)
            except Exception as ex:
                logger.error(f"Error calculating rounds in {self.model.__tablename__}: {ex}")
                return 0

        async def questions_actions(self):
            try:
                query_false = self.session.query(self.model).filter_by(questions_or_actions=False).all()
                query_true = self.session.query(self.model).filter_by(questions_or_actions=True).all()
                return {
                    "question": [qa.question_action for qa in query_false],
                    "action": [qa.question_action for qa in query_true]
                }
            except Exception as ex:
                logger.error(f"Error fetching questions/actions in {self.model.__tablename__}: {ex}")
                return {"question": [], "action": []}

    class Questions_Actions_From_Gamers(__Base):
        def __init__(self, session):
            super().__init__(session, QuestionActionFromGamer)

        async def create(self, id_gamer, question_action):
            try:
                new_qafg = self.model(id_gamer=id_gamer, question_action=question_action)
                self.session.add(new_qafg)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating in {self.model.__tablename__}: {ex}")
                return False

        async def update(self, id, id_gamer, question_action):
            try:
                qafg = self.session.query(self.model).filter_by(id=id).first()
                if qafg:
                    qafg.id_gamer = id_gamer
                    qafg.question_action = question_action
                    self.session.commit()
                    return True
                return False
            except Exception as ex:
                logger.error(f"Error updating in {self.model.__tablename__}: {ex}")
                return False

    class Answers(__Base):
        def __init__(self, session):
            super().__init__(session, Answer)

        async def create(self, id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score):
            try:
                new_answer = self.model(
                    id_game=id_game, id_gamer=id_gamer, id_question_action=id_question_action,
                    id_question_action_from_gamer=id_question_action_from_gamer, answer_start=answer_start,
                    answer_end=answer_end, score=score
                )
                self.session.add(new_answer)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating in {self.model.__tablename__}: {ex}")
                return False

        async def update(self, id, id_game, id_gamer, id_question_action, id_question_action_from_gamer, answer_start, answer_end, score):
            try:
                answer = self.session.query(self.model).filter_by(id=id).first()
                if answer:
                    answer.id_game = id_game
                    answer.id_gamer = id_gamer
                    answer.id_question_action = id_question_action
                    answer.id_question_action_from_gamer = id_question_action_from_gamer
                    answer.answer_start = answer_start
                    answer.answer_end = answer_end
                    answer.score = score
                    self.session.commit()
                    return True
                return False
            except Exception as ex:
                logger.error(f"Error updating in {self.model.__tablename__}: {ex}")
                return False

    class Participates(__Base):
        def __init__(self, session):
            super().__init__(session, Participate)

        async def create_connection(self, id_game, id_gamer):
            try:
                timing = datetime.now()
                new_participate = self.model(
                    id_game=id_game, id_gamer=id_gamer, connection_or_disconnection=False, timing=timing
                )
                self.session.add(new_participate)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating connection in {self.model.__tablename__}: {ex}")
                return False

        async def create_disconnection(self, id_game, id_gamer):
            try:
                timing = datetime.now()
                new_participate = self.model(
                    id_game=id_game, id_gamer=id_gamer, connection_or_disconnection=True, timing=timing
                )
                self.session.add(new_participate)
                self.session.commit()
                return True
            except Exception as ex:
                logger.error(f"Error creating disconnection in {self.model.__tablename__}: {ex}")
                return False

# Пример использования базы данных
if __name__ == "__main__":
    session = Session()

    # Примеры использования классов
    gamers_db = DataBase.Gamers(session)
    admins_db = DataBase.Admins(session)
    games_db = DataBase.Games(session)
    questions_actions_db = DataBase.Questions_Actions(session)
    questions_actions_from_gamers_db = DataBase.Questions_Actions_From_Gamers(session)
    answers_db = DataBase.Answers(session)
    participates_db = DataBase.Participates(session)

    # Примеры асинхронных вызовов функций
    import asyncio

    async def example_usage():
        await gamers_db.create(12345, 'example_user')
        exists = await gamers_db.is_exists(12345)
        print(f"Gamer exists: {exists}")

    asyncio.run(example_usage())
