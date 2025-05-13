# encoding=utf-8
import re
from bs4 import BeautifulSoup
import time
import requests

class ElecQuery:
    def __init__(self, username, password, base_url):
        """初始化查询对象，创建会话"""
        self.username = username
        self.password = password
        self.base_url = base_url
        self.session = requests.Session()  # 让会话全局有效

    def login(self):
        """登录系统"""
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
        """获取电费数据"""
        data_url = f"{self.base_url}dfcx/index.php?c=Dfcx&a=ydjl"
        res = self.session.get(data_url)  # **使用全局 session 发送请求**
        res_text = res.text

        # 解析 HTML，查找电费信息
        self.HTMLparser(res_text)

    def GenTimeStamp(self):
        """生成时间戳"""
        current_timestamp = int(time.time())
        print("当前时间戳为:", current_timestamp)

    def HTMLparser(self, res_text):
        """解析 HTML 并提取电费数据"""
        soup = BeautifulSoup(res_text, "html.parser")

        # 查找包含电费信息的 td 标签
        td_list = soup.find_all("td", style=lambda s: s and "font-size" in s)
        for td in td_list:
            text_data = td.text.strip()

            # 解析电表名称、剩余电量和总电量
            match = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", text_data)
            if match:
                meter_name = match.group(1)
                remaining_power = match.group(2)
                total_power = match.group(3)

                self.GenTimeStamp()  # 生成时间戳
                print(f"电表名称: {meter_name}")
                print(f"剩余电量: {remaining_power} 度")
                print(f"总电量: {total_power} 度")
            else:
                print("HTML匹配错误，可能是登录失败 ")