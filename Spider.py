import sys,os,requests,csv,re
sys.stdout.reconfigure(encoding='utf-8')
from datetime import timedelta, datetime
EndDate = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
StartDate = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
BaseUrl = "http://xyfw.xujc.com/"
import config
Username = config.username
Password = config.password
SessionFile = "Session.txt"
TimeFile = "SessionTime.txt"

class XyfwApi:
    def __init__(self):
        self.BaseUrl = BaseUrl
        self.Headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/58.0.3029.110 Safari/537.3")};
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
            from bs4 import BeautifulSoup
            Data, Now = [], datetime.now()
            Header, Printed = None, False

            for Offset in range(0, 180, 30):
                Start = (Now - timedelta(days=Offset + 30)).strftime("%Y-%m-%d")
                End = (Now - timedelta(days=Offset + 1)).strftime("%Y-%m-%d")

                for Page in [1, 2]:
                    Url = f"{self.BaseUrl}dfcx/index.php?c=Dfcx&a=ydjl&start={Start}&end={End}&page={Page}"
                    R = self.Session.get(Url, headers=self.Headers)
                    if R.status_code != 200:
                        continue
                    Soup = BeautifulSoup(R.text, "html.parser")
                    if not Printed:
                        for Td in Soup.find_all("td", style=lambda s: s and "font-size" in s):
                            M = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", Td.text.strip())
                            if M:
                                print(f"电表：{M[1]}, 剩余电量: {M[2]} 度, 总电量: {M[3]} 度")
                                Printed = True
                                break
                    Table = Soup.find("table", {"id": "data_table"})
                    if not Table:
                        continue
                    for Tr in Table.find_all("tr"):
                        Row = [Td.get_text(strip=True) for Td in Tr.find_all(["td", "th"])]
                        if Row and (Header is None or Row != Header):
                            if Header is None:
                                Header = Row
                            Data.append(Row)
            if Data:
                with open("ElecData.csv", "w", newline='', encoding="utf-8") as f:
                    csv.writer(f).writerows(Data)
            return True
        except Exception as e:
            print("错误:", e)
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

# class DataAnalysis:
#     def __init__(self, DataFile):
#         self.DataFile = DataFile
#         self.Data = []
#         self.LoadData()



if __name__ == "__main__":
    Api = XyfwApi()
    if Api.SessionManager.Expired():
        print("Session expired or missing, logging in...")
        if not Api.Login(Username, Password):
            print("Login failed. Check credentials.")
            # sys.exit(1)
        print("Login successful.")
    else:
        print("Using saved session.")
        Api.SessionManager.Load()
    ElecData = Api.FetchElecData()
    if ElecData:
        print("Electricity data fetched.")
    else:
        print("Failed to fetch electricity data.")
