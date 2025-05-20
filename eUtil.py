import time
import uuid
import requests
import pymongo
import re
from bs4 import BeautifulSoup

mongo_uri = "mongodb://localhost:27017"
client = pymongo.MongoClient(mongo_uri)
main_db = client["main_db"]
sessions = main_db["sessions"]
records = main_db["records"]

baseUrl = "http://xyfw.xujc.com/"
SESSION_TIMEOUT = 15 * 60

def GenTimeStamp():
    return int(time.time())

def eGenSession_id():
    return str(uuid.uuid4())

def eSaveSession(username, session_cookie, password, session_id=None):
    if not session_id:
        session_id = eGenSession_id()
    sessions.update_one(
        {"username": username},
        {"$set": {
            "session": session_cookie,
            "password": password,
            "timestamp": GenTimeStamp(),
            "session_id": session_id
        }},
        upsert=True
    )

def eGetSession(username):
    user_data = sessions.find_one({"username": username})
    if user_data:
        current_time = GenTimeStamp()
        session_time = user_data.get("timestamp", 0)
        if current_time - session_time > SESSION_TIMEOUT:
            new_session = eLogin(username, user_data.get("password"))
            new_session_id = eGenSession_id()
            if new_session:
                eSaveSession(username, new_session, user_data.get("password"), new_session_id)
                return {"session": new_session, "session_id": new_session_id}
            else:
                return None
        sid = user_data.get("session_id")
        if not sid:
            sid = eGenSession_id()
            sessions.update_one({"username": username}, {"$set": {"session_id": sid}})
        return {"session": user_data.get("session"), "session_id": sid}
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
    if session_data and session_data.get("session"):
        url = f"{baseUrl}dfcx/index.php?c=Dfcx&a=ydjl"
        return requests.get(url, cookies=session_data["session"]).text
    return None

def HTMLparser(res_text, username, session_id):
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
                "session_id": session_id
            }
            records.insert_one(record)
            result.append({
                "meter_id": match.group(1),
                "username": username,
                "remaining_power": match.group(2),
                "total_power": match.group(3),
                "timestamp": record["timestamp"]
            })
    return result
