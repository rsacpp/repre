#!/usr/bin/python3
import hashlib
import logging
import sqlite3
import socketserver
from subprocess import PIPE, Popen
from multiprocessing import Process
import logging

#submit a new proposal
def proposal(payload):
    pass

#fetch proposals with seqence number
def proposals(seq):
    pass

class Vip:
    def bootstrap(self):
        
class VipHandler(socketserver.BaseRequestHandler):
    def __init__(self):
        pass
    def bootstrap(self):
        con = sqlite3.connect('vip.db')
        cur = con.cursor()
        #table1:representative
        cur.execute('''CREATE TABLE representative(sha256 text primary key, seq bigint, ip text, port int, transactions_count bigint, f_count bigint) ''')
        cur.execute('''CREATE INDEX representative_seq on representative(seq)''')
        cur.execute('''CREATE INDEX representative__count on representative(transactions_count, f_count)''')
        #table2: id_request
        cur.execute('''CREATE TABLE id_request(seq bigint primary key, pq text, issued text)''')
        cur.execute('''CREATE INDEX id_request_pq on id_request(pq)''')
        #table3: transaction
        cur.execute('''CREATE TABLE transaction(seq bigint primary key, proposal text, verdict text, settled_in tinyint)''')
        cur.execute('''CREATE INDEX transaction_settled_in on transaction(settled_in)''')
        #table4: block
        cur.execute('''CREATE TABLE block(sha256 text primary key, chain text, seq bigint, raw text, total_transactions bigint, total_f bigint)''')
        cur.execute('''CREATE INDEX block_chain_seq on block(chain, seq)''')

        cur.execute('''CREATE TABLE chain(sha256 text primary key, refer_block text, refer_seq bigint, total_transactions bigint, total_f bigint)''')
        con.commit()
        con.close()

    def handle(self):
        length = self.request.recv(8).strip()
        length = int(str(length, 'utf-8'))
        payload = self.request.recv(length).strip()
        (code, payload) = payload.split('==>')
        if code == 'RequestID':
            p = Process(target=requestID, args=payload)
        if code == 'WriteID':
            p = Process(target=writeID, args=payload)
        if code == 'FetchID':
            p = Process(target=writeID, args=payload)
        if code == 'nodes':
            p = Process(target=nodes, args=payload)
        if code == 'Proposal':
            p = Process(target=proposal, args=payload)
        if code == 'Proposals':
            p = Process(target=proposals, args=payload)
        p.start()
        #p.join()

if __name__ == '__main__':
    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(process)d/\
%(thread)d %(pathname)s:%(lineno)s %(message)s"
    logging.basicConfig(filename='vip-debug.log', format=fmt0,
                        level=logging.DEBUG)    
    HOST, PORT = "", 12823
    with socketserver.TCPServer((HOST, PORT), VipHandler) as server:
        server.serve_forever()

