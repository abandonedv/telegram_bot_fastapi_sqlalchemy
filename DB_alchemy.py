import datetime

from sqlalchemy import Integer, String
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import select


class my_DB:
    engine = create_engine('sqlite:///messages_new.db', future=True)
    metadata = MetaData()
    conn = engine.connect()


    messages = Table('messages_new', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('message', String(50)),
                     Column('answer', String(50)),
                     Column('date', String(50)),
                     )

    async def insert_into_db(self, received: str, sent: str):
        with self.engine.begin() as db:
            obj = {"message": f"{received}",
                   "answer": f"{sent}",
                   "date": f"{datetime.datetime.now()}"}
            db.execute(self.messages.insert(), obj)

    async def get_from_db(self, num: int):
        with self.engine.begin() as db:
            r = db.execute(select(self.messages).where(self.messages.c.id == f"{num}"))
            res = r.fetchone()

            return res
