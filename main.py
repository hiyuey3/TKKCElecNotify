
# encoding=utf-8
import requests,re
from bs4 import BeautifulSoup
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
soup = BeautifulSoup(res_text, "html.parser")
td_list = soup.find_all("td", style=lambda s: s and "font-size" in s)
for td in td_list:
    text_data = td.text.strip()

    match = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", text_data)
    if match:
        meter_name = match.group(1)
        remaining_power = match.group(2)
        total_power = match.group(3)
        print(f"电表名称: {meter_name}")
        print(f"剩余电量: {remaining_power} 度")
        print(f"总电量: {total_power} 度")
        print("-" * 40)
