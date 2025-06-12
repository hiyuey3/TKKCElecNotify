import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import timedelta,datetime
endDate= (datetime.now()- timedelta(days=1)).strftime("%Y-%m-%d")
startDate = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
baseUrl="http://xyfw.xujc.com/"
username='eieu24053'
password='_tKk3M@K'
class xyfwApi:
    def __init__(self):
        self.baseUrl = baseUrl
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        self.session = requests.Session()
    def login(self, username, password):
        loginUrl = self.baseUrl + "dfcx/index.php?c=Login&a=login"
        data = {"username": username,"password": password}
        response = self.session.post(loginUrl, headers=self.headers, data=data)
        if response.status_code == 200:
            return response.text

        else:
            return False
    #dfcx/index.php?c=Dfcx&a=ydjl
    def fetchElecData(self):
        elecUrl = self.baseUrl + ("dfcx/index.php?c=Dfcx&a=ydjl&start=" + startDate + "&end=" + endDate+'&')
        response = self.session.get(elecUrl, headers=self.headers)
        if response.status_code == 200:
            return response.text
            with open("elecData"+endDate+".html", "w", encoding="utf-8") as file:
                file.write(ElecData)
        else:
            return None


if __name__ == "__main__":
    xyfw = xyfwApi()
    if xyfw.login(username, password):
        print("Login successful!")
        ElecData = xyfw.fetchElecData()
        if ElecData:
            print("Electricity data fetched successfully!")

        else:
            print("Failed to fetch electricity data.")
    else:
        print("Login failed. Please check your credentials.")