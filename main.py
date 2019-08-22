import os
import re
import json
import sqlalchemy as sa
from sqlalchemy.sql.selectable import Select
import logging
import threading
from sqlalchemy.orm import sessionmaker, scoped_session
from dbcreate import User,Command
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(thread)s - %(funcName)s - %(message)s')

def worker (user):
    logging.debug('Start worker')
    dangerous = ['chmod', 'sudo', 'reboot', 'sudo reboot']
##################TEST########################
    db_file = os.path.join(os.path.dirname(__file__), 'test.sqlite')
    engine = sa.create_engine('sqlite:///{}'.format(db_file), echo=False)
    connection = engine.connect()
    metadata = sa.MetaData()

    session = scoped_session(sessionmaker(bind=engine))
    users = sa.Table('user', metadata, autoload=True, autoload_with=engine)
    commands = sa.Table('command', metadata, autoload=True, autoload_with=engine)
    session = scoped_session(sessionmaker(bind=engine))



    query = sa.select([users]).where(users.columns.name == user)
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    print(ResultSet)

    res = connection.execute('Select * From command')
    Res = res.fetchall()
    print(Res)

###############################################

    os.chdir('/home/%s' % user)
    lock = threading.Lock()
    lock.acquire()
    try:
        f = open('.bash_history', 'r')
        lines = f.readlines()
        f.close()
    except Exception as e:
        logging.error(e)
        return
    finally:
        lock.release()
    logging.debug(len(lines))
    for line in lines:
        flag = False
        for item in dangerous:
            if line.startswith(item):
                flag = True
        #logging.debug(line)
        #cm = Command(user_id=ResultSet[0][0], command=line, is_dangerous=flag)
        #session.add(cm)
        #session.commit()




def main():
    logging.debug('main start')
    users = os.listdir('/home')
    logging.debug(users)
    for user in users:
        logging.debug('User: %s' % user)
        t = threading.Thread(target=worker, args=(user,))
        t.start()

main()