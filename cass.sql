
create table data_ring(row_id uuid primary key, clique int, sink text, lambda text, rangeFrom text, rangeTo text);
create custom index data_ring_clique on data_ring(clique) USING 'org.apache.cassandra.index.sasi.SASIIndex';
insert into data_ring(row_id, clique, sink, lambda, rangeFrom, rangeTo) values (now(), 0, 'cassandra://cluster1', ' & 0xffffffff', '0x0', '0x100000000');
--insert into data_ring(row_id, clique, sink, lambda, rangeFrom, rangeTo) values (now(), 32, 'mysql://mysql1', ' >>32 & 0xffffffff', '0x0', '0x80000000');
--insert into data_ring(row_id, clique, sink, lambda, rangeFrom, rangeTo) values (now(), 32, 'mysql://mysql2', ' >>32 & 0xffffffff', '0x80000000', '0x100000000');
--insert into data_ring(row_id, clique, sink, lambda, rangeFrom, rangeTo) values (now(), 64, 'postgresql://pg1', '>>64 & 0xffffffff', '0x0', '0x80000000');
--insert into data_ring(row_id, clique, sink, lambda, rangeFrom, rangeTo) values (now(), 64, 'postgresql://pg2', '>>64 & 0xffffffff', '0x80000000', '0x100000000');


create table
player3(sha256_id text primary key, symbol text, ver bigint,
pq0 text, d0 text, f0 text, pq1 text ,d1 text, f1 text, setup timestamp);

create table
blocks_view(sha256_id text primary key, block_id text, ver bigint,
raw text, sha256 text, nonce text, consent_algorithm text, predecessor text, counter bigint, setup  timestamp);

create table
transactions_view(sha256_id text primary key, verdict text, ver bigint,
pq text, raw_statement text, proposal text, symbol text, note_id text, quantity bigint, target text, block_id text, setup timestamp);

create table notes_view(sha256_id text primary key, note_id text, ver bigint,
symbol text, quantity bigint, holder text);

create custom index player3_symbol on player3(symbol)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index player3_ver on player3(ver)  USING 'org.apache.cassandra.index.sasi.SASIIndex';



create custom index blocks_view_id on blocks_view(block_id)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index blocks_view_ver on blocks_view(ver)  USING 'org.apache.cassandra.index.sasi.SASIIndex';
create custom index blocks_view_counter on blocks_view(counter)  USING 'org.apache.cassandra.index.sasi.SASIIndex';


create custom index transactions_view_ver on transactions_view(ver)  USING 'org.apache.cassandra.index.sasi.SASIIndex';
create custom index transactions_view_symbol on transactions_view(symbol)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index transactions_view_note_id on transactions_view(note_id)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index transactions_view_quantity on transactions_view(quantity)  USING 'org.apache.cassandra.index.sasi.SASIIndex';
create custom index transactions_view_target on transactions_view(target)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index transactions_view_block_id on transactions_view(block_id)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};


create custom index notes_view_note_id on notes_view(note_id)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index notes_view_ver on notes_view(ver)  USING 'org.apache.cassandra.index.sasi.SASIIndex' ;
create custom index notes_view_note_symbol on notes_view(symbol)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};
create custom index notes_view_note_quantity on notes_view(quantity)  USING 'org.apache.cassandra.index.sasi.SASIIndex';
create custom index notes_view_note_holder on notes_view(holder)  USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'true'};



create table draft(sha256_id text primary key, note_id text, ver bigint,
symbol text, quantity bigint, target text, refer text
);

create table candidate(sha256_id text primary key, proposal text, ver bigint,
pq text, verdict text, target text, refer text
);
