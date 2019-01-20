#!/usr/bin/env python3
#fileencoding: utf-8

#-----------------------------------------------#
# python standard library
#-----------------------------------------------#
import calendar
import csv
from enum import Enum
from datetime import datetime as dt

#-----------------------------------------------#
# pip
#-----------------------------------------------#
from oauth2client import tools

#-----------------------------------------------#
# my lib
#-----------------------------------------------#
import gspread
from zaimapi import ZaimAPI, ZaimLocalDB

class Payer(Enum):
    UNKNOWN = 0
    alpha = 1
    beta = 2

class PaymentFmt:
    Header = []
    Header.append("日付")
    Header.append("カテゴリ")
    Header.append("ジャンル")
    Header.append("商品名")
    Header.append("メモ")
    Header.append("場所")
    Header.append("支出額")
    Header.append("alpha支払額")
    Header.append("beta支払額")
    Header.append("alpha負担額")
    Header.append("beta負担額")
    Header.append("alpha個人用")
    Header.append("beta個人用")
    def __init__(self):
        pass

class Payment:
    def __init__(self, date, category, genre, name, comment, place, price):
        self.date = date
        self.category = category
        self.genre = genre
        self.name = name
        self.comment = comment
        self.place = place
        self.price = price
        self.alpha_paid = 0
        self.beta_paid = 0
        self.alpha_owe = 0
        self.beta_owe = 0
        self.alpha_self_paid = 0
        self.beta_self_paid = 0
        self.id_paid = 0
        self._set_paid()
        self._set_owe()

    def __repr__(self):
        return " ".join([str(i) for i in self.to_list()])

    def _pay_for_myself(self):
        return "個人_" in self.category

    def is_for_oneself(self):
        return self._pay_for_myself()

    def _who_paid(self):
        if "_alpha" in self.category:
            return Payer.alpha
        elif "_beta" in self.category:
            return Payer.beta
        else:
            return Payer.UNKNOWN

    def _paid_by_id(self):
        if "id" == self.comment.strip().split("\n")[0]:
            return True
        else:
            return False

    def get_normalized_category(self):
        return self.category.replace("_alpha", "").replace("_beta", "").replace("個人_", "")

    def _set_paid(self):
        if self._who_paid() == Payer.alpha:
            if self._pay_for_myself():
                self.alpha_self_paid += self.price
            else:
                self.alpha_paid += self.price
        elif self._who_paid() == Payer.beta:
            if self._pay_for_myself():
                self.beta_self_paid += self.price
            else:
                self.beta_paid += self.price
        else:
            self.beta_paid = self.price // 2
            self.alpha_paid = self.price - self.beta_paid

    def _set_owe(self):
        if self._pay_for_myself():
            return

        if "dp" == self.comment.strip().split("\n")[0]:
            return

        category = self.get_normalized_category()
        genre = self.genre
        self.beta_owe = self.price // 2
        self.alpha_owe = self.price - self.beta_owe

    def get_date(self):
        return self.date

    def get_date_str(self):
        return "{}-{:02d}".format(self.date.year, self.date.month)

    def get_category(self):
        return self.category

    def get_genre(self):
        return self.genre

    def get_name(self):
        return self.name

    def get_place(self):
        return self.place

    def get_price(self):
        return self.price

    def get_alpha_paid(self):
        return self.alpha_paid

    def get_beta_paid(self):
        return self.beta_paid

    def get_alpha_owe(self):
        return self.alpha_owe

    def get_beta_owe(self):
        return self.beta_owe

    def get_alpha_self_paid(self):
        return self.alpha_self_paid

    def get_beta_self_paid(self):
        return self.beta_self_paid

    def to_list(self):
        ret = []
        ret.append("{}-{}-{}".format(self.date.year, self.date.month, self.date.day))
        ret.append(self.category)
        ret.append(self.genre)
        ret.append(self.name)
        ret.append(self.comment)
        ret.append(self.place)
        ret.append(self.price)
        ret.append(self.alpha_paid)
        ret.append(self.beta_paid)
        ret.append(self.alpha_owe)
        ret.append(self.beta_owe)
        ret.append(self.alpha_self_paid)
        ret.append(self.beta_self_paid)
        return ret

class PaymentSummary:
    def __init__(self):
        self.payments = []
        self.category_total = {}
        self.alpha_category_total = {}
        self.beta_category_total = {}
        self.alpha_paid = 0
        self.beta_paid = 0
        self.alpha_owe = 0
        self.beta_owe = 0
        self.alpha_self_paid = 0
        self.beta_self_paid = 0

    def append(self, pay):
        self.payments.append(pay)
        ncat = pay.get_normalized_category()
        if not pay.is_for_oneself():
            self.category_total[ncat] = self.category_total.get(ncat, 0) + pay.get_price()
            self.alpha_paid += pay.get_alpha_paid()
            self.beta_paid += pay.get_beta_paid()
            self.alpha_owe += pay.get_alpha_owe()
            self.beta_owe += pay.get_beta_owe()
        else:
            self.alpha_category_total[ncat] = self.alpha_category_total.get(ncat, 0) + pay.get_alpha_self_paid()
            self.beta_category_total[ncat] = self.beta_category_total.get(ncat, 0) + pay.get_beta_self_paid()
            self.alpha_self_paid += pay.get_alpha_self_paid()
            self.beta_self_paid += pay.get_beta_self_paid()

    def get_category_total(self):
        return self.category_total

    def get_alpha_category_total(self):
        return self.alpha_category_total

    def get_beta_category_total(self):
        return self.beta_category_total

    def get_alpha_paid_total(self):
        return self.alpha_paid

    def get_beta_paid_total(self):
        return self.beta_paid

    def get_alpha_owe_total(self):
        return self.alpha_owe

    def get_beta_owe_total(self):
        return self.beta_owe

    def get_alpha_self_paid_total(self):
        return self.alpha_self_paid

    def get_beta_self_paid_total(self):
        return self.beta_self_paid


def read_csv(filename):
    payments = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        header = next(f)
        for r in reader:
            date = dt.strptime(r[0], "%Y-%m-%d")
            category = r[2]
            genre = r[3]
            name = r[6]
            place = r[8]
            comment = r[9]
            price = int(r[11])
            payments.append(Payment(date, category, genre, name, comment, place, price))
    return payments

def get_data_by_api(apikey_filename, start_date, end_date):
    z = ZaimAPI(apikey_filename)
    print("(1/1) Get data by Zaim REST API")
    entries = z.get_entries(start_date, end_date)
    return entries

def update_local_db(entries, this_month):
    zldb = ZaimLocalDB("./zaim.db")
    print("(1/2) delete entries in {}".format(this_month))
    zldb.delete_entries_by_date(this_month)
    print("(2/2) update entries in {}".format(this_month))
    zldb.update_entries(entries)

def gen_payments(entries):
    payments = []
    for r in entries[::-1]:
        date = dt.strptime(r["date"], "%Y-%m-%d")
        category = r["category"]
        genre = r["genre"]
        name = r["name"]
        place = r["place"]
        price = int(r["amount"])
        comment = r["comment"]
        payments.append(Payment(date, category, genre, name, comment, place, price))
    return payments

def gen_reqvalues(pay_lists):
    summary = PaymentSummary()
    for p in pay_lists:
        summary.append(p)

    alpha_paid = summary.get_alpha_paid_total()
    beta_paid = summary.get_beta_paid_total()
    alpha_owe = summary.get_alpha_owe_total()
    beta_owe = summary.get_beta_owe_total()
    alpha_self_paid = summary.get_alpha_self_paid_total()
    beta_self_paid = summary.get_beta_self_paid_total()

    values = []
    values.append(["■支払額"])
    values.append(["alpha支払い額", alpha_paid, "=sum(h:h)"])
    values.append(["beta支払い額", beta_paid, "=sum(i:i)"])
    values.append(["合計", alpha_paid + beta_paid, "=sum(c2:c3)"])
    values.append([""])
    values.append(["■負担額"])
    values.append(["alpha負担額", alpha_owe, "=sum(j:j)"])
    values.append(["beta負担額", beta_owe, "=sum(k:k)"])
    print("total_paid:", alpha_paid+beta_paid)
    print("alpha_paid:", alpha_paid)
    print("beta_paid:", beta_paid)
    print("alpha_owe:", alpha_owe)
    print("beta_owe:", beta_owe)

    diff = alpha_paid - alpha_owe
    if diff >= 0:
        print("beta -> alpha:", diff)
        values.append(["清算(betaからalpha)", diff, "=c2-c7"])
    else:
        print("alpha -> beta:", diff)
        values.append(["清算(alphaからbeta)", diff, "=c7-c2"])
    values.append([""])

    values.append(["■カテゴリ別合計"])
    for k, v in summary.get_category_total().items():
        values.append([k, v])
    values.append([""])

    values.append(["■ 個人会計"])
    values.append(["alpha個人合計", alpha_self_paid])
    for k, v in summary.get_alpha_category_total().items():
        values.append([k, v])
    values.append([""])

    values.append(["beta個人会計", beta_self_paid])
    for k, v in summary.get_beta_category_total().items():
        values.append([k, v])
    values.append([""])

    values.append(["■全エントリ"])
    values.append(PaymentFmt.Header)
    for p in pay_lists:
        values.append(p.to_list())

    return values

#-----------------------------------------------#
def main():
    n = dt.now()
    start_default = "{}-{:02d}-01".format(n.year, n.month)
    end_default = "{}-{:02d}-{:02d}".format(n.year, n.month, calendar.monthrange(n.year, n.month)[1])
    try:
        import argparse
        parent_parser = argparse.ArgumentParser(parents=[tools.argparser])
        parent_parser.add_argument("--credential", type=str, default="sheets.googleapis.my-kakeibo.json")
        parent_parser.add_argument("--start", type=str, default=start_default)
        parent_parser.add_argument("--end", type=str, default=end_default)
        parent_parser.add_argument("--zaimapikey", type=str, default="zaim_secret.json")
        parent_parser.add_argument("--csv", type=str, default="")
        parent_parser.add_argument("--spreadsheet", action="store_true")
        flags = parent_parser.parse_args()
    except ImportError:
        flags = None

    print("span: ", flags.start, flags.end)
    if flags.spreadsheet == True:
        num_of_steps = 4
    else:
        num_of_steps = 3

    if flags.csv != "":
        print("************* Start parsing CSV file *************")
        pay_lists = read_csv(flags.csv)
        print("*************  End parsing CSV file  *************")
    else:
        print("[1/{}] Get data from Zaim".format(num_of_steps))
        entries = get_data_by_api(flags.zaimapikey, flags.start, flags.end)
        print("[2/{}] Update local DB".format(num_of_steps))
        this_month = flags.start[:7]
        update_local_db(entries, this_month)
        print("[3/{}] Calc payments".format(num_of_steps))
        pay_lists = gen_payments(entries)
    values = gen_reqvalues(pay_lists)
    values.append([""])
    print("")
    if flags.spreadsheet:
        print("[4/{}] Send data to Google Spreadsheet".format(num_of_steps))
        print("sheet_name:", pay_lists[0].get_date_str())
        #print(values)
        g = gspread.Gspread(flags)
        print("(1/2) create a sheet whose name is {}".format(pay_lists[0].get_date_str()))
        result = g.create_new_sheet(pay_lists[0].get_date_str())
        print(result) # fixme: check result
        sheet_name = pay_lists[0].get_date_str()
        start_column = "A"
        end_column = chr(ord("A") + len(PaymentFmt.Header))
        range_name = "{}!{}:{}".format(sheet_name, start_column, end_column)
        print("range_name:", range_name)
        value_input_option = "USER_ENTERED"
        print("(2/2) append data to the sheet")
        result = g.append_data(range_name, value_input_option, values)
        print(result) # fixme: check result

if __name__ == "__main__":
    main()
