import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3


class ElecQuery:
    def __init__(self, username, password, base_url, sqlite_db="elec_records.db"):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.session = requests.Session()
        # self.openid = openid
        self.db = sqlite3.connect(sqlite_db)
        self.cursor = self.db.cursor()
        self.msg = ''

        # 创建表格（如果不存在的话）
        self.create_table()

    def create_table(self):
        # 创建记录表格
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS elec_records
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                timestamp
                                INTEGER,
                                meter_name
                                TEXT,
                                remaining_power
                                REAL,
                                total_power
                                REAL
                            )
                            """)
        self.db.commit()

    def login(self):
        login_url = f"{self.base_url}dfcx/index.php?c=Login&a=login"
        login_data = {"username": self.username, "password": self.password}
        response = self.session.post(login_url, data=login_data)

        if "登录失败" in response.text:
            print("登录失败，请检查用户名和密码")
            return False
        else:
            print("登录成功")
            return True

    def fetch_data(self):
        data_url = f"{self.base_url}dfcx/index.php?c=Dfcx&a=ydjl"
        res = self.session.get(data_url)
        res_text = res.text
        self.HTMLparser(res_text)

    def GenTimeStamp(self):
        return int(time.time())

    def store_data(self, meter_name, remaining_power, total_power):
        timestamp = self.GenTimeStamp()
        data = (timestamp, meter_name, float(remaining_power), float(total_power))

        # 插入数据到 SQLite 数据库
        self.cursor.execute("""
                            INSERT INTO elec_records (timestamp, meter_name, remaining_power, total_power)
                            VALUES (?, ?, ?, ?)
                            """, data)
        self.db.commit()

        print("数据已存入 SQLite, 等待下次执行")

    def compare_previous(self, meter_name, current_remaining, total_power):
        # 查询 SQLite 数据库中最新的记录
        self.cursor.execute("""
                            SELECT remaining_power
                            FROM elec_records
                            WHERE meter_name = ?
                            ORDER BY timestamp DESC LIMIT 1
                            """, (meter_name,))
        latest = self.cursor.fetchone()

        if latest:
            last_remaining = latest[0]
            change = float(current_remaining) - last_remaining
            print('电表：', meter_name)
            print(f"上次记录的剩余电量: {last_remaining} 度")
            print(f"电量变化: {change} 度")
            # self.SendMsg('电表：'+meter_name+f"<br />剩余电量: {last_remaining} 度<br />" +f"电量变少: {int(change)} 度")
        else:
            print("无历史数据的对比会在下次开始")

    def HTMLparser(self, res_text):
        soup = BeautifulSoup(res_text, "html.parser")
        td_list = soup.find_all("td", style=lambda s: s and "font-size" in s)
        for td in td_list:
            text_data = td.text.strip()
            match = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", text_data)
            if match:
                meter_name = match.group(1)
                remaining_power = match.group(2)
                total_power = match.group(3)

                self.compare_previous(meter_name, remaining_power, total_power)
                self.store_data(meter_name, remaining_power, total_power)
                print("-" * 40)
            else:
                print("匹配错误")

    # def SendMsg(msg, openid):
    #     requests.post('https://push.xyw.cx/weixin.php', data={'msg': msg, 'openid': openid})
