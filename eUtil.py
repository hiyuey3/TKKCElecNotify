import time
import uuid
import requests
import pymongo
import re
from bs4 import BeautifulSoup
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
headers = {
    'User-Agent': USER_AGENT
}

post_headers = {
    'User-Agent': USER_AGENT,
    'Content-Type': "application/x-www-form-urlencoded"
}


# mongo_uri = "mongodb://localhost:27017"
client = pymongo.MongoClient("mongodb://localhost:27017")
main_db = client["main_db"]
mdb_session = main_db["sessions"]
mdb_records = main_db["records"]

baseUrl = "http://xyfw.xujc.com/"
SESSION_TIMEOUT = 15 * 60

def GenTimeStamp():
    return int(time.time())

def eGenSession_id():
    return str(uuid.uuid4())

def eSaveSession(username, session_cookie, password, e_session_id=None):
    if not e_session_id:
        e_session_id = eGenSession_id()
    mdb_session.update_one(
        {"username": username},
        {"$set": {
            "e_session": session_cookie,
            "password": password,
            "timestamp": GenTimeStamp(),
            "e_session_id": e_session_id
        }},
        upsert=True
    )

def eGetSession(username):
    user_data = mdb_session.find_one({"username": username})
    if user_data:
        current_time = GenTimeStamp()
        session_time = user_data.get("timestamp", 0)
        if current_time - session_time > SESSION_TIMEOUT:
            new_session = eLogin(username, user_data.get("password"))
            new_session_id = eGenSession_id()
            if new_session:
                eSaveSession(username, new_session, user_data.get("password"), new_session_id)
                return {"e_session": new_session, "e_session_id": new_session_id}
            else:
                return None
        sid = user_data.get("e_session_id")
        if not sid:
            sid = eGenSession_id()
            mdb_session.update_one({"username": username}, {"$set": {"e_session_id": sid}})
        return {"e_session": user_data.get("e_session"), "e_session_id": sid}
    return None

def eLogin(username, password):
    if not password:
        return None
    s = requests.Session()
    response = s.post(
        f"{baseUrl}dfcx/index.php?c=Login&a=login",
        data={"username": username, "password": password}
    )
    return None if "登录失败" in response.text else s.cookies.get_dict()

def eFetchData(username):
    session_data = eGetSession(username)
    if session_data and session_data.get("e_session"):
        url = f"{baseUrl}dfcx/index.php?c=Dfcx&a=ydjl"
        return requests.get(url, cookies=session_data["e_session"]).text
    return None

# def HTMLparser(res_text, username, session_id):
#     soup = BeautifulSoup(res_text, "html.parser")
#     result = []
#     for td in soup.find_all("td", style=lambda s: s and "font-size" in s):
#         match = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", td.text.strip())
#         if match:
#             record = {
#                 "meter_id": match.group(1),
#                 "username": username,
#                 "remaining_power": match.group(2),
#                 "total_power": match.group(3),
#                 "timestamp": GenTimeStamp(),
#                 "e_session_id": session_id
#             }
#             mdb_records.insert_one(record)
#             # mdb_records.update_one({"username": username}, {"$set": record})
#             result.append({
#                 "meter_id": match.group(1),
#                 "username": username,
#                 "remaining_power": match.group(2),
#                 "total_power": match.group(3),
#                 "timestamp": record["timestamp"]
#             })
#     return result
def HTMLparser(res_text, username, e_session_id):
    soup = BeautifulSoup(res_text, "html.parser")
    result = []
    for td in soup.find_all("td", style=lambda s: s and "font-size" in s):
        match = re.search(r"(.+?)：购买剩余电量 (\d+\.\d+) 度，总电量 (\d+\.\d+) 度", td.text.strip())
        if match:
            record = {
                "meter_id": match.group(1),
                "username": username,
                "remaining_power": match.group(2),
                "total_power": match.group(3),
                "timestamp": GenTimeStamp(),
                "e_session_id": e_session_id
            }
            mdb_records.update_one(
                {"username": username},
                {"$set": record},
                upsert=True  # 如果不存在就插入
            )
            result.append(record)
    return result