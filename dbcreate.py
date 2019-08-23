from sqlalchemy import  create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
import os


metadata = MetaData()
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    is_root = Column(BOOLEAN)

    commands = relationship('Command')

    def __repr__(self):
        return "<User(id = '%s', name='%s')>" % (self.id, self.name)

class Command(Base):
    __tablename__ = 'command'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    command = Column(String(512))
    is_dangerous = Column(BOOLEAN)

    users = relationship('User')


#Setup
db_file = os.path.join(os.path.dirname(__file__), 'test.sqlite')
engine = create_engine('sqlite:///{}'.format(db_file), echo=False)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = scoped_session(sessionmaker(bind=engine))
"""
u1 = User(name='bill')
session.add(u1)
session.commit()

u2 = User(name='bill2', is_root=False)
session.add(u2)
session.commit()

c1 = Command(user_id=u2.id, command='chmode', is_dangerous=False)
session.add(c1)
session.commit()
"""