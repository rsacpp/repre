#!/usr/bin/python3
import sqlite3
import argparse
import socketserver
from multiprocessing import Process
from subprocess import Popen, PIPE

transf = lambda x: ''.join(reversed(x)).lower().replace(':', '')


class Senate(socketserver.BaseRequestHandler):
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
        local_pq text, local_e text)''')

        # senate keys
        bns = []
        cmd = '/usr/bin/openssl', 'genrsa', '3072'
        parseCmd = '/usr/bin/openssl', 'asn1parse'

        with Popen(cmd, stdout=PIPE) as p:
            with Popen(parseCmd, stdin=PIPE, stdout=PIPE) as p2:
                output = str(p2.communicate(input=p.stdout.read())[0], 'utf-8')
                for a in output.split('INTEGER'):
                    bns.extend(list(filter(lambda x: x.startswith("           :"), a.splitlines())))
                senatePq = transf(bns[1])
                senateD = transf(bns[3])
                cur.execute("""
                insert into credential(pq, d, e) values('{0}', '{1}', '{2}')
                """.format(senatePq, senateD, '10001'))
                con.commit()
                con.close()

    def requestID(self, local_pq):
        cmd = './openssl', 'genrsa', '2048'
        parseCmd = '/usr/bin/openssl', 'asn1parse'
        output = ''
        pqKey, dKey, jgKey = '', '', ''
        bns = []
        with Popen(cmd, stdout=PIPE) as p:
            with Popen(parseCmd, stdin=PIPE, stdout=PIPE) as p2:
                output = str(p2.communicate(input=p.stdout.read())[0], 'utf-8')
                for a in output.split('INTEGER'):
                    bns.extend(list(filter(lambda x: x.startswith("           :"), a.splitlines())))
                pqKey = transf(bns[1])
                dKey = transf(bns[3])
                jgKey = transf(bns[-1])
        pqKey = pqKey.strip()
        dKey = dKey.strip()
        jgKey = jgKey.strip()

        self.cur.execute("""
        insert into pal(pq, f, e, local_pq, local_e)
        values('{0}','{1}','{2}','{3}','{4}','{5}')
        """.format(pqKey, jgKey, '11001', local_pq, '10001'))

        stmt = """select pq, d from credential"""
        self.cur.execute(stmt)
        [senatePq, senateD] = self.cur.fetchone()
        encryptedPq, encryptedD = '', ''

        encrypt = './crypt', local_pq, '10001', pqKey
        with Popen(encrypt, stdout=PIPE) as p:
            encryptedPq = str(p.stdout.read().strip(), 'utf-8')
        encrypt = './crypt', senatePq, senateD, encryptedPq
        with Popen(encrypt, stdout=PIPE) as p:
            encryptedPq = str(p.stdout.read().strip(), 'utf-8')

        encrypt = './crypt', local_pq, '10001', dKey
        with Popen(encrypt, stdout=PIPE) as p:
            encryptedD = str(p.stdout.read().strip(), 'utf-8')
        encrypt = './crypt', senatePq, senateD, encryptedD
        with Popen(encrypt, stdout=PIPE) as p:
            encryptedD = str(p.stdout.read().strip(), 'utf-8')
        # local_pq for retrieval
        self.cur.execute("""
        insert into local(pq, d, local_pq) values ('{0}', '{1}', '{2}')
        """.format(encryptedPq, encryptedD, local_pq))
        self.con.commit()

    def fetchID(self, local_pq):
        # encrypted*
        stmt = """
        select pq, d from local where local_pq = '{0}' """.format(local_pq)
        self.cur.execute(stmt)
        [encryptedPq, encryptedD] = self.cur.fetchone()
        if not encryptedPq:
            return ''

        # SenatePQ
        stmt = """select pq from credential"""
        self.cur.execute(stmt)
        [senatePq] = self.cur.fetchone()
        if senatePq:
            return '^^{0}||{1}||{2}$$'.format(senatePq, encryptedPq, encryptedD)
        else:
            return '^^$$'


class SenateHandler(socketserver.BaseRequestHandler):
    def __init__(self):
        self.senate = Senate()

    def handle(self):
        length = int(str(self.request.recv(8).strip(), 'utf-8'))
        payload = str(self.request.recv(length).strip(), 'utf-8')
        (code, arg) = payload.split('==>')
        if code == 'RequestID':
            p = Process(target=self.senate.requestID, args=arg)
            p.start()
        # return the new id
        if code == 'FetchID':
            output = self.senate.fetchID(arg)
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bootstrap', action='store_true')
    args = parser.parse_args()
    s = Senate(args.bootstrap)

    host, port = 'localhost', 12821
    with socketserver.TCPServer((host, port), SenateHandler) as server:
        server.serve_forever()
