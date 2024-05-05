from pymongo import MongoClient
import os
admin_login = os.environ.get("Stock_MongoDB_Admin_Login")
admin_pw = os.environ.get("Stock_MongoDB_Admin_PW")


def get_db_handle(db_name='stock_records_db', host="localhost", port=27017, username=admin_login, password=admin_pw):

    client = MongoClient(host=host,
                         port=int(port),
                         username=username,
                         password=password
                         )
    db_handle = client[db_name]
    return db_handle, client
