import sys,os,requests,csv,re
sys.stdout.reconfigure(encoding='utf-8')
from datetime import timedelta, datetime
EndDate = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
StartDate = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
BaseUrl = "http://xyfw.xujc.com/"
Username = 'eieu24053'
Password = '_tKk3M@K'
SessionFile = "Session.txt"
TimeFile = "SessionTime.txt"

class XyfwApi:
    def __init__(self):
        self.BaseUrl = BaseUrl
        self.Headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
            )
        }
        self.Session = requests.Session()
        self.SessionManager = SessionManager(self.Session, SessionFile, TimeFile)
    def Login(self, Username, Password):
        LoginUrl = self.BaseUrl + "dfcx/index.php?c=Login&a=login"
        Data = {"username": Username, "password": Password}
        try:
            R = self.Session.post(LoginUrl, headers=self.Headers, data=Data)
            if R.status_code == 200 and "欢迎您" in R.text:
                self.SessionManager.Save()
                return True
            else:
                return False
        except:
            return False

    def FetchElecData(self):
        try:
            Data = []
            from bs4 import BeautifulSoup
            for Page in [1, 2]:
                ElecUrl = self.BaseUrl + f"dfcx/index.php?c=Dfcx&a=ydjl&start={StartDate}&end={EndDate}&page={Page}"
                R = self.Session.get(ElecUrl, headers=self.Headers)
                if R.status_code != 200:
                    return None
                with open("ElecData" + EndDate + "_Page" + str(Page) + ".html", "w", encoding="utf-8") as F:
                    F.write(R.text)
                Soup = BeautifulSoup(R.text, 'html.parser')
                for Td in Soup.find_all("td", style=lambda s: s and "font-size" in s):
                    Match = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", Td.text.strip())
                    if Match:
                        MeterName, RemainingPower, TotalPower = Match.groups()
                        print(f"电表：{MeterName}, 剩余电量: {RemainingPower} 度, 总电量: {TotalPower} 度")
                Table = Soup.find('table', {'id': 'data_table'})
                Rows = Table.find_all('tr')
                for i, Tr in enumerate(Rows):
                    if Page == 2 and i == 0:
                        continue
                    Cols = Tr.find_all(['td', 'th'])
                    Row = [Td.get_text(strip=True) for Td in Cols]
                    if Row:
                        Data.append(Row)
            with open("ElecData.csv", "w+", newline='', encoding="utf-8") as F:
                csv.writer(F).writerows(Data)
            return R.text
        except Exception as E:
            print(f"错误: {E}")
            return None


class SessionManager:
    def __init__(self, Session, SessionFile, TimeFile):
        self.Session = Session
        self.SessionFile = SessionFile
        self.TimeFile = TimeFile
    def Save(self):
        with open(self.SessionFile, "w+", encoding="utf-8") as f:
            for cookie in self.Session.cookies:
                f.write(f"{cookie.name}={cookie.value}\n")
        with open(self.TimeFile, "w+") as f:
            f.write(datetime.now().isoformat())
    def Load(self):
        if os.path.exists(self.SessionFile):
            with open(self.SessionFile, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        name, value = line.strip().split("=", 1)
                        self.Session.cookies.set(name, value)
    def Expired(self, MaxHours=3):
        if not os.path.exists(self.TimeFile):
            return True
        with open(self.TimeFile, "r") as f:
            try:
                ts = datetime.fromisoformat(f.read())
                return datetime.now() - ts > timedelta(hours=MaxHours)
            except:
                return True

class DataAnalysis:
    def __init__(self, DataFile):
        self.DataFile = DataFile
        self.Data = []
        self.LoadData()


if __name__ == "__main__":
    Api = XyfwApi()
    if Api.SessionManager.Expired():
        print("Session expired or missing, logging in...")
        if not Api.Login(Username, Password):
            print("Login failed. Check credentials.")
            sys.exit(1)
        print("Login successful.")
    else:
        print("Using saved session.")
        Api.SessionManager.Load()
    ElecData = Api.FetchElecData()
    if ElecData:
        print("Electricity data fetched.")
    else:
        print("Failed to fetch electricity data.")
