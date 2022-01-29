import sqlite3
from subprocess import Popen, PIPE

con = sqlite3.connect('a2.db')
cur = con.cursor()
cur.execute('''
CREATE TABLE credential(pq text primary key, d text, e text)
''')

bns = []
cmd = '/usr/bin/openssl', 'genrsa', '3072'
parseCmd = '/usr/bin/openssl', 'asn1parse'
transf = lambda x: ''.join(reversed(x)).lower().replace(':', '')
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

cur.execute('select pq, d, e from credential')
[pq, d, e] = cur.fetchone()
print('{} {} {}'.format(pq, d, e))

