#!/usr/bin/python
import psycopg2
from config import config
import datetime
from psycopg2 import sql


logger = None

def connect(cur_logger):
    """ Connect to the PostgreSQL database server """
    params = config()
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)

    global logger
    logger = cur_logger
    return conn

def disconnect(conn):
    conn.close()
    print('Database connection closed.')

#string formating for psycopg2, for testing purposes only
def executeSQL(conn,insert_stmt):
    try:
        cur = conn.cursor()

        try:
            cur.execute(insert_stmt)
        #usually triggered by duplicate due to primary key
        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        else:
            conn.commit()

        cur.close()
        return True 
    except Exception as e:
        logger.error(e[0])
        return False




def insertPost(conn,id,provider_id,provider_name,published_at,summary,title,url,time):
    try:
        cur = conn.cursor()

        try:
            cur.execute(
    sql.SQL("insert into {} values (%s, %s, %s, %s, %s, %s, %s, %s)")
        .format(sql.Identifier('yahoo_posts')),
    [id,provider_id,provider_name,published_at,summary,title,url,time])

        #usually triggered by duplicate due to primary key
        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        else:
            conn.commit()

        cur.close()
        return True 
    except Exception as e:
        logger.error(str(e))
        return False

def main():
    with connect() as conn:
        executeSQL(conn,"INSERT INTO testtable (id) VALUES ('test1');")
        disconnect(conn)
if __name__ == '__main__':
    main()
