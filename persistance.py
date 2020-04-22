from sqlalchemy import Column, Integer, String, DateTime, BOOLEAN
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, load_only
import datetime
from sqlalchemy.sql import text

Base = declarative_base()


class Following(Base):
    __tablename__ = 'following'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id=Column(String(250), primary_key=True)
    user_id = Column(String(50), nullable=False)
    username = Column(String(250), nullable=False)
    iteration = Column(Integer, default=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class Persistence:
    def __init__(self, username):
        # Create an engine that stores data in the local directory's
        # sqlalchemy_example.db file.
        self._engine = create_engine('sqlite:///spy_{}.db'.format(username))

        # Create all tables in the engine. This is equivalent to "Create Table"
        # statements in raw SQL.
        Base.metadata.create_all(self._engine)

        self._Session = sessionmaker(bind=self._engine)
        self._session = self._Session()

    def get_current_iteration(self):
        max = self._session.query(func.max(Following.iteration)).scalar()
        if max is None:
            return 0

        return max

    def save_following(self, following):
        self._session.merge(following)
        self._session.commit()

    def delete_all_iteration(self, iteration):
        delete_q = Following.__table__.delete().where(Following.iteration == iteration)
        self._session.execute(delete_q)
        self._session.commit()

    def get_stopped_following(self, current_iteration, last_iteration):
        result = self._session.execute(
            'SELECT username FROM following WHERE iteration=:previous AND username not in (select username from following where iteration=:current)',
            {'current': current_iteration, 'previous': last_iteration})

        return [row[0] for row in result]

    def get_started_following(self, current_iteration, last_iteration):
        result = self._session.execute(
            'SELECT * FROM following WHERE iteration == :current AND username not in (select username from following where iteration ==:previous)',
            {'current': current_iteration, 'previous': last_iteration})

        return [row[0] for row in result]