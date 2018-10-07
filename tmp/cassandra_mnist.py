###Use the following python program in order to create a keyspace and a table inside it.###
import logging

log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

KEYSPACE = "mnist"

def createKeySpace():
    cluster = Cluster(contact_points=['0.0.0.0'],port=9042)
    session = cluster.connect()

    log.info("Creating keyspace...")
    try:
        session.execute("""
            CREATE KEYSPACE %s
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
            """ % KEYSPACE)

        log.info("setting keyspace...")
        session.set_keyspace(KEYSPACE)

        log.info("creating table...")
        session.execute("""
            CREATE TABLE mnist_test (
                Time timestamp,
                filename text,
                result int,
                PRIMARY KEY (Time, filename)
            )
            """)
    except Exception as e:
        log.error("Unable to create keyspace")
        log.error(e)

#createKeySpace();


###Delete the created table###

def deleteTable():
    cluster = Cluster(contact_points=['0.0.0.0'],port=9042)
    session = cluster.connect()

    log.info("setting keyspace...")
    session.set_keyspace(KEYSPACE)

    try:
        log.info("Deleting a table...")
        session.execute('''DROP TABLE mnist_test''')
    except Exception as e:
        log.error("Unable to delete a table")
        log.error(e)


###Delete the created keyspace###

def deleteKeyspace():
    cluster = Cluster(contact_points=['0.0.0.0'],port=9042)
    session = cluster.connect()

    try:
        log.info("Deleting a keyspace...")
        session.execute('''DROP KEYSPACE %s''' % KEYSPACE)
    except Exception as e:
        log.error("Unable to delete a keyspace")
        log.error(e)


###Insert timestamp, file name and results in table###

def insertData(time, filename, result):
    cluster = Cluster(contact_points=['0.0.0.0'],port=9042)
    session = cluster.connect()

    log.info("setting keyspace...")
    session.set_keyspace(KEYSPACE)

    prepared = session.prepare("""
    INSERT INTO mnist_test (Time, filename, result)
    VALUES (?, ?, ?)
    """)

    log.info("inserting into mnist_test")
    session.execute(prepared.bind((dateof(now()), filename, result)))

###Reading the freshly inserted data is not that difficult using a function similar to the one below:###

def readRows():
    cluster = Cluster(contact_points=['0.0.0.0'],port=9042)
    session = cluster.connect()

    log.info("setting keyspace...")
    session.set_keyspace(KEYSPACE)

    rows = session.execute("SELECT * FROM mnist_test")
    log.info("key\tfilename\tresult")
    log.info("---------\t----\t----")

    count=0
    for row in rows:
        if(count%100==0):
            log.info('\t'.join(row))
        count=count+1

    log.info("Total")
    log.info("-----")
    log.info("rows %d" %(count))
