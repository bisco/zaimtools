#!/usr/bin/env python3

import sqlite3

def dbgen():
    conn = sqlite3.connect("zaim.db")
    c = conn.cursor()

    create_table_query = """
    create table zaim_kakeibo(
        zaim_id integer primary key not null,
        user_id integer,
        receipt_id integer,
        mode integer,
        date text,
        category_id integer,
        category text,
        genre_id integer,
        genre text,
        amount integer,
        currency_code text,
        name text,
        place_uid text,
        place text,
        comment text,
        created text,
        active integer,
        from_account_id integer,
        to_account_id integer
    )
    """
    c.execute(create_table_query)
    conn.commit()
    conn.close()

dbgen()
