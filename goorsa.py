#!/usr/bin/python3
from subprocess import Popen, PIPE
import hashlib
import uuid
import socket
import time


def transfer(text):
    return ''.join(reversed(text)).lower().replace(':', '').strip()


def generateNumbers(bits, e):
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


def verify(dat, nonce, final):
    cmd = './mining' dat, nonce
    with Popen(cmd, stdout=PIPE) as p:
        output = p.stdout.read().strip()
        return output == final


def countF(dat):
    counter = 0
    for c in dat:
        if c == 'f':
            counter += 1
        else:
            return counter


def newRuntime(bits):
    return generateNumbers(bits, '10001')[:2]


def requstID(senate='senate.goorsa.com'):
    runtimePq, runtimeD = newRuntime(2560)
    dat = 'RequestID==>{0}'.format(runtimePq)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((senate, 12821))
        length = len(dat)
        sock.send(bytes('{:08}'.format(length), 'utf-8'))
        sock.send(bytes(dat, 'utf-8'))
    # loop until ID is retrieved
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((senate, 12821))
            dat = 'FetchID==>{0}'.format(runtimePq)
            length = len(dat)
            sock.send(bytes('{:08}'.format(length), 'utf-8'))
            sock.send(bytes(dat, 'utf-8'))
            length = int(str(sock.recv(8).strip(), 'utf-8'))
            payload = str(sock.recv(length).strip(), 'utf-8')
            if payload == '^$':
                time.sleep(8)
            else:
                [senatePq, encryptedPq, encryptedD] = payload.split('||')
                senatePq = senatePq.split('^')[-1]
                encryptedD = encryptedD.split('$')[0]

                encryptedPq = calc(senatePq, '10001', encryptedPq)
                clique3pq = calc(runtimePq, runtimeD, encryptedPq)

                encryptedD = calc(senatePq, '10001', encryptedD)
                clique3d = calc(runtimePq, runtimeD, encryptedD)
                # total 6 numbers, first 3 for runtime, later 3 for clique3
                return runtimePq, runtimeD, '10001', clique3pq, clique3d, '30001'
