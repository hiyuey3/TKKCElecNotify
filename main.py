# encoding=utf-8
import Util
from config import *


if __name__ == "__main__":
    eq = Util.ElecQuery(username, password, baseUrl)
    if eq.login():
        eq.fetch_data()