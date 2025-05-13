# encoding=utf-8
import requests
import Util
from config import *
baseUrl = "http://xyfw.xujc.com/"
session = requests.Session()
session.post(baseUrl + "dfcx/index.php?c=Login&a=login", data={"username": username, "password": password})
res = session.get(baseUrl + "dfcx/index.php?c=Dfcx&a=ydjl").text
Util.HTMLparser(res)