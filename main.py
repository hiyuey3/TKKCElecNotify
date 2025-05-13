# encoding=utf-8
import Util
from config import *


if __name__ == "__main__":
    print("-" * 40)
    print('嘉庚学院电费查询')
    eq = Util.ElecQuery(username, password, baseUrl,mongo_uri)
    if eq.login():
        eq.fetch_data()