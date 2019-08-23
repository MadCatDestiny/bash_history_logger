import os
import re
import json
import sqlalchemy as sa
from sqlalchemy.sql.selectable import Select
import logging
import threading
from sqlalchemy.orm import sessionmaker, scoped_session
from dbcreate import User, Command
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(thread)s - %(funcName)s - %(message)s')

def worker (user):
    logging.debug('Start worker')
    dangerous = ['chmod', 'sudo', 'reboot', 'sudo reboot']

    try:
        os.chdir('/home/%s' % user)
        f = open('.bash_history', 'r')
        lines = f.readlines()
        f.close()
    except Exception as e:
        logging.error(e)
        return

    db_file = os.path.join(os.path.dirname(__file__), 'test.sqlite')
    engine = sa.create_engine('sqlite:///{}'.format(db_file), echo=False)
    connection = engine.connect()
    metadata = sa.MetaData()
    logging.debug(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    users = sa.Table('user', metadata, autoload=True, autoload_with=engine)
    #commands = sa.Table('command', metadata, autoload=True, autoload_with=engine)
    #query = sa.select([users]).where(users.columns.name == user)
    query = session.query(User).filter(User.name == user)
    if len(query.all()) == 0:
        u = User(name= user)
        session.add(u)
        session.commit()

    ResultSet = []
    for i in session.query(User).filter(User.name == user):
        logging.debug(str([i.id, i.name]))
        ResultSet.append([i.id, i.name])

    logging.debug(len(lines))
    val_list = []

    for line in lines:
        flag = False
        for item in dangerous:
            if line.startswith(item):
                flag = True

        #logging.debug(line)
        comm = Command(user_id=ResultSet[0][0], command=line, is_dangerous=flag)
        val_list.append(comm)

    session.add_all(val_list)
    session.commit()
    logging.debug('session.commit()')
    logging.debug(connection.execute('Select * From command').fetchmany(10))


def main():
    logging.debug('main start')
    users = os.listdir('/home')
    logging.debug(users)
    for user in users:
        #logging.debug('User: %s' % user)
        #t = threading.Thread(target=worker, args=(user,))
        #t.start()
        worker(user)

main()