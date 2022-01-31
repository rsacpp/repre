#!/usr/bin/python3
from subprocess import Popen, PIPE
import hashlib
import uuid


def transfer(text):
    return ''.join(reversed(text)).lower().replace(':', '').strip()


def generateNumbers(self, bits, e):
    bns = []
    if e == '10001':
        cmd = '/usr/bin/openssl', 'genrsa', '{0}'.format(bits)
    if e == '30001':
        cmd = './openssl', 'genrsa', '{0}'.format(bits)
    parseCmd = '/usr/bin/openssl', 'asn1parse'
    with Popen(cmd, stdout=PIPE) as p:
        with Popen(parseCmd, stdin=PIPE, stdout=PIPE) as p2:
            output = str(p2.communicate(input=p.stdout.read())[0], 'utf-8')
            for a in output.split('INTEGER'):
                bns.extend(list(filter(lambda x: x.startswith("           :"), a.splitlines())))
            pq = transfer(bns[1])
            d = transfer(bns[3])
            jgKey = transfer(bns[-1])
            return pq, d, jgKey


def calc(pq, factor, val):
    cmd = './crypt', pq, factor, val
    with Popen(cmd, stdout=PIPE) as p:
        return str(p.stdout.read().strip(), 'utf-8')


def sha256(dat):
    m = hashlib.sha256()
    m.update(bytes(dat, 'utf-8'))
    return m.hexdigest()


def mining(dat, tag):
    randomhex = uuid.uuid4().hex
    cmd = './mining', dat, randomhex
    while True:
        with Popen(cmd, stdout=PIPE) as p:
            output = p.stdout.read().strip()
            if output.startswith(tag):
                return randomhex, output


def countF(self, dat):
    counter = 0
    for c in dat:
        if c == 'f':
            counter += 1
        else:
            return counter
