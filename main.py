import os
import re
import json
import sqlalchemy as sa
import logging
import threading
from sqlalchemy.orm import sessionmaker
from dbcreate import User, Command
import argparse
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(thread)s - %(funcName)s - %(message)s')

def worker (user):
    logging.debug('Start worker')
    dangerous = ['chmod', 'sudo', 'reboot', 'sudo reboot']

    try:
        path = os.getcwd()
        os.chdir('/home/%s' % user)
        f = open('.bash_history', 'r')
        lines = f.readlines()
        f.close()
        os.chdir(path)
    except Exception as e:
        logging.error(e)
        return
    path = os.path.realpath(__file__)
    logging.debug(path)
    db_file = os.path.join(os.path.dirname(path), 'test.sqlite')
    logging.debug(db_file)
    engine = sa.create_engine('sqlite:///{}'.format(db_file), echo=False)
    connection = engine.connect()
    metadata = sa.MetaData()
    #users = sa.Table('user', metadata, autoload=True, autoload_with=engine)
    logging.debug(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(User).filter(User.name == user)
    logging.debug(query)
    logging.debug(query.all())
    if len(query.all()) == 0:
        root = is_root(user)
        u = User(name=user, is_root=root)
        session.add(u)
        session.commit()
        logging.debug(session)

    ResultSet = []
    for i in session.query(User).filter(User.name == user):
        logging.debug(str([i.id, i.name, i.is_root]))
        ResultSet.append([i.id, i.name, i.is_root])

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


def is_root(user):
    data = ['sudo', 'root', 'admin']
    for item in data:
        os.system('cat /etc/group | grep %s > log.txt' % item)
        with open('log.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                splited = line.split(':')
                logging.debug(splited)
                if splited[-1] == user+'\n':
                    return True
    os.system('rm log.txt')

    return False


def dangerous():
    db_file = os.path.join(os.path.dirname(__file__), 'test.sqlite')
    if os.path.exists(db_file):
        engine = sa.create_engine('sqlite:///{}'.format(db_file), echo=False)
        connection = engine.connect()
        metadata = sa.MetaData()
        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(User,Command.command).join(Command).filter(User.is_root == 0 and Command.is_dangerous == 1)
        if len(query.all()) == 0:
            print('None')
            return
        else:
            for i in query:
                print(i[0].id, i[0].name, i[1], sep=' : ')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dangerous', help='Show the names of users who tried to use the dangerous command',action='count')

    args = parser.parse_args()
    if args.dangerous:
        dangerous()
    else:
        logging.debug('main start')
        users = os.listdir('/home')
        logging.debug(users)
        for user in users:
            worker(user)


if __name__ == '__main__':
    main()