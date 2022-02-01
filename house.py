#!/usr/bin/python3
import sqlite3
import argparse
import socketserver
import hashlib
import uuid
from multiprocessing import Process
from subprocess import Popen, PIPE
import logging
import goorsa


class House:
    def bootstrap(self):
        con = sqlite3.connect('house.db')
        cur = con.cursor()
        statements = """
        CREATE TABLE block(sha256 text primary key, raw text, nonce text, final text, chain text, seq bigint,
        transaction_count bigint, f_count bigint) ;
        CREATE TABLE chain(sha256 text primary key, refer text, refer_seq bigint, block_count bigint, transaction_count bigint, f_count bigint)
        ;
        CREATE TABLE transaction(sha256 text primary key, verdict text, proposal text, raw text, block_refer text, transaction_refer text)
        ;
        CREATE TABLE representative(runtime_pq text primary key, runtime_d text, runtime_e text, senator_pq text,
        clique3pq text, clique3d text, clique3e text)
        """
        for s in statements.split(';'):
            logging.info('executing {0}'.format(s))
            cur.execute(s)
        # set up the representative
        senatePq, runtimePq, runtimeD, e, clique3pq, clique3d, clique3e = goorsa.requestID('senate.goorsa.com')
        cur.execute("""
        INSERT INTO representative(runtime_pq, runtime_d, runtime_e, clique3pq, clique3d, clique3e)
        values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
        """.format(runtimePq, runtimeD, e, clique3Pq, clique3d, clique3e))
        self.clique3pq = clique3pq

        # genesis block 'In God We Trust'
        raw = 'In God We Trust[representative:{0}]'.format(self.representative())
        shaCode = goorsa.sha256(raw)
        nonce, final = goorsa.mining(shaCode, 'f')
        cur.execute("""
        INSERT INTO block (sha256, raw, nonce, final, chain, seq) values(
        '{0}', '{1}', '{2}', '{3}', '{4}', {5})
        """.format(shaCode, raw, nonce, final, shaCode, 1))
        cur.execute("""
        INSERT INTO chain (sha256, refer, refer_seq, block_count, transaction_count, f_count) values(
        '{0}', '', 0, 1, 0, {1})
        """.format(shaCode, goorsa.countF(final)))
        con.commit()
        con.close()

    def load(self):
        self.cur.execute("""
        select sha256, block_count, transaction_count, f_count from chain order by transaction_count, f_count desc limit 1
        """)
        [self.currentChain, self.blockCount, self.transactionCount, self.fCount] = self.cur.fetchone()
        self.cur.execute("""
        select sha256 from block where chain='{0}' order by seq desc limit 1
        """)
        [self.blockPtr] = self.cur.fetchone()
        # load runtime
        self.cur.execute("""
        select clique3pq from runtime
        """)
        self.representativePq = self.cur.fetchone()[0]
        logging.debug('representativePq = {0}'.format(self.representativePq))

    def stat(self):
        # report the name/length/transaction_count/f_count of the longest chain
        return self.currentChain, self.blockCount, self.transactionCount, self.fCount

    def fetchBlock(seq):
        self.fetchBlock(self.currentChain, seq)

    def fetchBlock(chain, seq):
        self.cur.execute("""
        select refer_seq, refer from chain where sha256='{0}'
        """.format(chain))
        [minSeq, parentChain] = self.cur.fetchone()
        # if the seq is on current chain
        if minSeq <= seq:
            self.cur.execute("""
            select sha256, raw, nonce, final from block where chain='{0}' and seq={1}
            """)
            return self.cur.fetchone()
        # othewise goto its parent
        else:
            return self.fetchBlock(parentChain, seq)

    def blockRefer(raw):
        # get the refer of the block
        pass

    def sanityCheck(block):
        # sanity check of the block
        sha256, raw, nonce, final = block
        # layout of raw:
        # (/prevBlock/Nonce/final)[transactions]{representative:##}
        if not goorsa.sha256(raw) == sha256:
            return False
        if not goorsa.verify(sha256, nonce, final):
            return False

    def applyBlock(block):
        bSha256, bRaw, bNonce, bFinal = block
        blockRefer = self.blockRefer(bRaw)
        if blockRefer == self.blockPtr:
            if self.sanityCheck(block):
                # update the chain& block
                pass

    def __init__(self, bootstrap):
        if bootstrap:
            self.bootstrap()
        self.con = sqlite3.connect('house.db')
        self.cur = self.con.cursor()
        self.loadChain()
        while True:
            # provision the chain with proposal/verdicts


if __name__ == '__main__':
    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(process)d/\
%(thread)d %(pathname)s:%(lineno)s %(message)s"
    logging.basicConfig(filename='house-debug.log', format=fmt0,
                        level=logging.DEBUG)
