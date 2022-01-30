#!/usr/bin/python3
import sqlite3
import logging
import socket
import time
import argparse
from subprocess import Popen, PIPE

transf = lambda x: ''.join(reversed(x)).lower().replace(':', '').strip()


class Pal:
    def genNumbers(self, bits):
        bns = []
        cmd = '/usr/bin/openssl', 'genrsa', '{0}'.format(bits)
        parseCmd = '/usr/bin/openssl', 'asn1parse'
        with Popen(cmd, stdout=PIPE) as p:
            with Popen(parseCmd, stdin=PIPE, stdout=PIPE) as p2:
                output = str(p2.communicate(input=p.stdout.read())[0], 'utf-8')
                for a in output.split('INTEGER'):
                    bns.extend(list(filter(lambda x: x.startswith("           :"), a.splitlines())))
                pq = transf(bns[1])
                d = transf(bns[3])
                e = '10001'
                return pq, d, e

    def calc(self, pq, factor, val):
        cmd = './crypt', pq, factor, val
        with Popen(cmd, stdout=PIPE) as p:
            return str(p.stdout.read().strip(), 'utf-8')

    def bootstrap(self, senate, representative):
        con = sqlite3.connect('pal.db')
        cur = con.cursor()
        # table0: credential
        cur.execute("""
        CREATE TABLE credential(local_pq text primary key, local_d text, local_e text, pq text, d text, e text)
        """)
        local_pq, local_d, e = self.genNumbers(2560)
        cur.execute("""
        INSERT INTO credential(local_pq, local_d, local_e) values ('{0}', '{1}', '{2}')
        """.format(local_pq, local_d, e))
        dat = 'RequestID==>{0}'.format(local_pq)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((senate, 12821))
            length = len(dat)
            sock.send(bytes('{:08}'.format(length), 'utf-8'))
            sock.send(bytes(dat, 'utf-8'))
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((senate, 12821))
                dat = 'FetchID==>{0}'.format(local_pq)
                length = len(dat)
                sock.send(bytes('{:08}'.format(length), 'utf-8'))
                sock.send(bytes(dat, 'utf-8'))
                length = int(str(sock.recv(8).strip(), 'utf-8'))
                payload = str(sock.recv(length).strip(), 'utf-8')
                if payload == '^$':
                    time.sleep(8)
                else:
                    # ^SenatePQ||PQ||D$
                    [senatePq, encryptedPq, encryptedD] = payload.split('||')
                    senatePq = senatePq.split('^')[-1]
                    encryptedD = encryptedD.split('$')[0]

                    encryptedPq = self.calc(senatePq, '10001', encryptedPq)
                    thePq = self.calc(local_pq, local_d, encryptedPq)

                    encryptedD = self.calc(senatePq, '10001', encryptedD)
                    theD = self.calc(local_pq, local_d, encryptedD)
                    cur.execute("""
                    UPDATE credential set pq='{0}', d='{1}', e='{2}' where local_pq ='{3}'
                    """.format(thePq, theD, '30001', local_pq))
                    break
        con.commit()
        con.close()

    def __init__(self, senate, house, bootstrap):
        if bootstrap:
            self.bootstrap(senate, house)


if __name__ == '__main__':
    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(process)d/\
%(thread)d %(pathname)s:%(lineno)s %(message)s"
    logging.basicConfig(filename='pal-debug.log', format=fmt0,
                        level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bootstrap', action='store_true')
    parser.add_argument('--senate', default='senate.goorsa.com')
    parser.add_argument('--house', default='house.goorsa.com')
    args = parser.parse_args()
    p = Pal(args.senate, args.house, args.bootstrap)
