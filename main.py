# encoding=utf-8
import requests
import Util
username = ""
password = ""
baseUrl = "http://xyfw.xujc.com/"
session = requests.Session()
login_url = baseUrl + "dfcx/index.php?c=Login&a=login"
login_data = {"username": username, "password": password}
session.post(login_url, data=login_data)
data_url = baseUrl + "dfcx/index.php?c=Dfcx&a=ydjl"
res = session.get(data_url)
res_text = res.text
Util.HTMLparser(res_text)
