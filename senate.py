#!/usr/bin/python3
import sqlite3
import argparse
import socketserver
from multiprocessing import Process
import logging
import goorsa


class Senate:
    def __init__(self, bootstrap):
        if bootstrap:
            self.bootstrap()
        self.con = sqlite3.connect('senate.db')
        self.cur = self.con.cursor()

    def bootstrap(self):
        con = sqlite3.connect('senate.db')
        cur = con.cursor()
        # table0: credential
        cur.execute('''
        CREATE TABLE credential(pq text primary key, d text, e text)
        ''')
        # table1: pal
        cur.execute('''
        CREATE TABLE pal(pq text primary key, f text, e text,
        local_pq text, local_e text)
        ''')
        # table2: local
        cur.execute('''
        CREATE TABLE local(local_pq text primary key, pq text, d text)
        ''')

        # senate keys
        senatePq, senateD = goorsa.generateNumbers(3072, '10001')[:2]
        cur.execute("""
        insert into credential(pq, d, e) values('{0}', '{1}', '{2}')
        """.format(senatePq, senateD, '10001'))
        con.commit()
        con.close()

    def requestID(self, local_pq):
        logging.debug('local_pq={}'.format(local_pq))
        pqKey, dKey, jgKey = goorsa.generateNumbers(2048, '30001')
        self.cur.execute("""
        insert into pal(pq, f, e, local_pq, local_e)
        values('{0}','{1}','{2}','{3}','{4}')
        """.format(pqKey, jgKey, '30001', local_pq, '10001'))

        stmt = """select pq, d from credential"""
        self.cur.execute(stmt)
        [senatePq, senateD] = self.cur.fetchone()
        encryptedPq, encryptedD = '', ''
        # local public sign
        encryptedPq = goorsa.calc(local_pq, '10001', pqKey)
        # senate private sign
        encryptedPq = goorsa.calc(senatePq, senateD, encryptedPq)

        # local public sign
        encryptedD = goorsa.calc(local_pq, '10001', dKey)
        # senate private sign
        encryptedD = goorsa.calc(senatePq, senateD, encryptedD)
        # local_pq for retrieval
        self.cur.execute("""
        insert into local(pq, d, local_pq) values ('{0}', '{1}', '{2}')
        """.format(encryptedPq, encryptedD, local_pq))
        self.con.commit()

    def fetchID(self, local_pq):
        # encrypted*
        stmt = """
        select pq, d from local where local_pq = '{0}'
        """.format(local_pq.strip())
        self.cur.execute(stmt)
        [encryptedPq, encryptedD] = self.cur.fetchone()
        if not encryptedPq:
            return ''

        # SenatePQ
        stmt = """select pq from credential"""
        self.cur.execute(stmt)
        [senatePq] = self.cur.fetchone()
        if senatePq:
            return '^{0}||{1}||{2}$'.format(senatePq, encryptedPq, encryptedD)
        else:
            return '^$'


class SenateHandler(socketserver.BaseRequestHandler):
    def handle(self):
        length = int(str(self.request.recv(8).strip(), 'utf-8'))
        payload = str(self.request.recv(length).strip(), 'utf-8')
        (code, arg) = payload.split('==>')
        logging.debug('{0}==>{1}'.format(code, arg))
        if code == 'RequestID':
            p = Process(target=senate.requestID, args=(arg,))
            p.start()
        # return the new id
        if code == 'FetchID':
            output = senate.fetchID(arg)
            logging.debug('output = {0}'.format(output))
            length = len(output)
            # send the length
            self.request.send(bytes('{:08}'.format(length), 'utf-8'))
            # send the payload
            self.request.send(bytes(output, 'utf-8'))
        if code == 'Proposal':
            pass
        if code == 'RawBlock':
            pass


if __name__ == '__main__':
    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(process)d/\
%(thread)d %(pathname)s:%(lineno)s %(message)s"
    logging.basicConfig(filename='senate-debug.log', format=fmt0,
                        level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bootstrap', action='store_true')
    args = parser.parse_args()
    senate = Senate(args.bootstrap)

    host, port = 'localhost', 12821
    with socketserver.TCPServer((host, port), SenateHandler) as server:
        server.serve_forever()
