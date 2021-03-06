#!/usr/bin/env python3
#fileencoding: utf-8

#----------------------------------------#
# python standard library
#----------------------------------------#
import json
import os
import sqlite3

#----------------------------------------#
# pip
#----------------------------------------#
import requests
from requests_oauthlib import OAuth1

class ZaimAPI:
    GET_MONEY_URL = u"https://api.zaim.net/v2/home/money"
    GET_CATEGORY_URL = u"https://api.zaim.net/v2/home/category"
    GET_GENRE_URL = u"https://api.zaim.net/v2/home/genre"

    def __init__(self, filename="zaim_secret.json"):
        credential_dir = os.path.join(os.path.abspath(os.path.curdir), ".credentials")
        credential_path = os.path.join(credential_dir, filename)
        with open(credential_path, "r") as f:
            key_data = json.load(f)
            ZaimAPI.CONSUMER_KEY = key_data["CONSUMER_KEY"]
            ZaimAPI.CONSUMER_SECRET = key_data["CONSUMER_SECRET"]
            ZaimAPI.ACCESS_TOKEN = key_data["ACCESS_TOKEN"]
            ZaimAPI.ACCESS_TOKEN_SECRET = key_data["ACCESS_TOKEN_SECRET"]

        self.__oauth_header = OAuth1(ZaimAPI.CONSUMER_KEY,
                                     ZaimAPI.CONSUMER_SECRET,
                                     ZaimAPI.ACCESS_TOKEN,
                                     ZaimAPI.ACCESS_TOKEN_SECRET,
                                     signature_type='auth_header')
        self.categories = self.__gen_idname_dict(ZaimAPI.GET_CATEGORY_URL, "categories")
        self.genres = self.__gen_idname_dict(ZaimAPI.GET_GENRE_URL, "genres")

    def __gen_idname_dict(self, url, key):
        params = { "mapping" : "1" }
        r = requests.get(url, auth=self.__oauth_header, params=params)
        _d = r.json()[key]
        d = {}
        for i in _d:
            d[i["id"]] = i["name"]
        return d

    def get_category(self, cat_id):
        return self.categories[cat_id]

    def get_genre(self, genre_id):
        return self.genres[genre_id]

    def get_entries(self, start_date, end_date):
        params = {
            "mapping" : "1",
            "mode" : "payment",
            "start_date" : start_date,
            "end_date" : end_date,
        }
        r = requests.get(self.GET_MONEY_URL, auth=self.__oauth_header, params=params)
        entries = r.json()["money"]
        for e in entries:
            e["category"] = self.get_category(e["category_id"])
            e["genre"] = self.get_genre(e["genre_id"])
        return entries

    def dump_json(self, start_date, end_date):
        if self.entries == False:
            self.get_entries(start_date, end_date)
        with open("output_{}_{}.json".format(start_date, end_date), "w") as f:
            json.dump(self.entries, f)

class ZaimLocalDB:
    def __init__(self, db_path="./zaim.db"):
        self.db_path = os.path.abspath(db_path)
        self.db_conn = sqlite3.connect(self.db_path)
        self.db_cursor = self.db_conn.cursor()

    def db_commit(self):
        self.db_conn.commit()

    def db_close(self):
        self.db_close()

    def exec_query(self, q, k=None):
        if k == None:
            self.db_cursor.execute(q)
        else:
            self.db_cursor.execute(q, k)

    def delete_entries_by_date(self, start_year_month):
        delete_query = 'DELETE FROM zaim_kakeibo where date like "{}%"'.format(start_year_month)
        self.exec_query(delete_query)

    def update_entries(self, entries):
        insert_query = """
        REPLACE INTO zaim_kakeibo
            (
                zaim_id,
                user_id,
                receipt_id,
                mode,
                date,
                category_id,
                category,
                genre_id,
                genre,
                amount,
                currency_code,
                name,
                place_uid,
                place,
                comment,
                created,
                active,
                from_account_id,
                to_account_id
            )
        VALUES
            (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
          """
        keys = [
                "id",
                "user_id",
                "receipt_id",
                "mode",
                "date",
                "category_id",
                "category",
                "genre_id",
                "genre",
                "amount",
                "currency_code",
                "name",
                "place_uid",
                "place",
                "comment",
                "created",
                "active",
                "from_account_id",
                "to_account_id"
               ]
        for entry in entries:
            key = [entry[k] for k in keys]
            self.exec_query(insert_query, key)

def main():
    import datetime, sys
    if len(sys.argv) == 2:
        start_date = sys.argv[1]
    else:
        start_date = "2017-01-01"
    print(start_date)
    sys.exit(1)
    z = ZaimAPI()
    today = datetime.datetime.today()
    this_month = datetime.datetime(today.year, today.month, 1)
    last_month = this_month + datetime.timedelta(days = -1)
    entries = z.get_entries(start_date, last_month.strftime("%Y-%m-%d"))
    z.update_db()

if __name__ == "__main__":
    main()
