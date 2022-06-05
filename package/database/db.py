from multiprocessing.sharedctypes import Value
import psycopg2
import os
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv(dotenv_path="config")
        self.dbname=os.getenv("DB_NAME")
        self.user=os.getenv("DB_USER")
        self.password=os.getenv("DB_PASS")
        self.host=os.getenv("DB_HOST")
        self.port = 5432

    def __connect__(self):
        self.con = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host, port = self.port)
        self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def fetch(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    def execute(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        self.con.commit()
        self.__disconnect__()

        
