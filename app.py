from flask import Flask, request, jsonify
import requests
import pymongo
import uuid
import time
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

mongo_uri = "mongodb://localhost:27017"
client = pymongo.MongoClient(mongo_uri)
user_db = client["user_db"]
users = user_db["users"]
main_db = client["main_db"]
sessions = main_db["sessions"]
records = main_db["records"]

baseUrl = "http://xyfw.xujc.com/"
SESSION_TIMEOUT = 15 * 60

def GenTimeStamp():
    return int(time.time())

def generate_session_id():
    return str(uuid.uuid4())

def store_user(username, password, wx_openid, wx_unionid, wx_nickname):
    users.update_one(
        {"username": username},
        {"$set": {
            "password": password,
            "wx_openid": wx_openid,
            "wx_unionid": wx_unionid,
            "wx_nickname": wx_nickname,
            "created_at": GenTimeStamp()
        }},
        upsert=True
    )

# @app.route('/saveUser', methods=['POST'])
# def api_save_user():
#     data = request.json
#     username = data.get("username")
#     password = data.get("password")
#     wx_openid = data.get("wx_openid")
#     wx_unionid = data.get("wx_unionid")
#     wx_nickname = data.get("wx_nickname")
#
#     if not username or not password:
#         return jsonify({"status": "error", "message": "缺少用户名或密码"}), 400
#
#     store_user(username, password, wx_openid, wx_unionid, wx_nickname)
#     return jsonify({"status": "success", "message": "用户信息已保存（微信已关联）"})
#
def store_session(username, session_cookie, password, session_id=None):
    if not session_id:
        session_id = generate_session_id()
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

def get_session(username):
    user_data = sessions.find_one({"username": username})
    if user_data:
        current_time = GenTimeStamp()
        session_time = user_data.get("timestamp", 0)
        if current_time - session_time > SESSION_TIMEOUT:
            # 会话过期，重新登录
            print(f"用户 {username} 的 session 已过期，重新登录...")
            new_session = login(username, user_data.get("password"))
            new_session_id = generate_session_id()
            if new_session:
                store_session(username, new_session, user_data.get("password"), new_session_id)
                return {"session": new_session, "session_id": new_session_id}
            else:
                return None
        # 如果记录中没有 session_id，则生成并更新
        sid = user_data.get("session_id")
        if not sid:
            sid = generate_session_id()
            sessions.update_one({"username": username}, {"$set": {"session_id": sid}})
        return {"session": user_data.get("session"), "session_id": sid}
    return None

def login(username, password):
    """
    使用用户名和密码登录（用于电费查询）。
    登录成功返回 session cookies，否则返回 None。
    """
    if not password:
        return None
    s = requests.Session()
    response = s.post(
        f"{baseUrl}dfcx/index.php?c=Login&a=login",
        data={"username": username, "password": password}
    )
    if "登录失败" in response.text:
        return None
    return s.cookies.get_dict()

@app.route('/api/eLogin', methods=['POST'])
def api_login():
    """
    /login 接口：电费查询登录 API
    请求需包含 "username" 和 "password"。
    如果 sessions 表中已有记录且未过期则直接返回，否则重新登录更新记录。
    返回 JSON 包含 "status"、"message" 及当前会话的 "session_id"（保证不为 null）。
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    session_data = get_session(username)
    if not session_data:
        # 若无记录，则尝试登录
        new_session = login(username, password)
        if new_session:
            new_session_id = generate_session_id()
            store_session(username, new_session, password, new_session_id)
            session_data = {"session": new_session, "session_id": new_session_id}
        else:
            return jsonify({"status": "error", "message": "登录失败"}), 401

    return jsonify({
        "status": "success",
        "message": "登录成功",
        "session_id": session_data["session_id"]
    })

def fetch_data(username):
    """
    使用当前有效的 session 获取电费查询页面的 HTML 数据。
    """
    session_data = get_session(username)
    if session_data and session_data.get("session"):
        url = f"{baseUrl}dfcx/index.php?c=Dfcx&a=ydjl"
        return requests.get(url, cookies=session_data["session"]).text
    return None

def HTMLparser(res_text, username, session_id):
    """
    解析 HTML 数据，抽取电量信息（剩余电量、总电量）。
    同时将解析结果存入 records 表中，每条记录中保存 session_id。
    返回解析后的数据列表（不包含 session_id，可由外层返回）。
    """
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
            # 返回给客户端时不必包含 session_id 信息
            record_data = {
                "meter_id": match.group(1),
                "username": username,
                "remaining_power": match.group(2),
                "total_power": match.group(3),
                "timestamp": record["timestamp"]
            }
            result.append(record_data)
    return result

@app.route('/api/eQuery', methods=['POST'])
def api_query():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"status": "error", "message": "缺少 username 参数"}), 400

    session_data = get_session(username)
    if not session_data:
        return jsonify({"status": "error", "message": "会话无效或未登录"}), 401

    current_session_id = session_data["session_id"]
    docs = list(records.find({"username": username, "session_id": current_session_id}, {"_id": 0}))
    if not docs:

        res_text = fetch_data(username)
        if res_text:
            HTMLparser(res_text, username, current_session_id)
            docs = list(records.find({"username": username, "session_id": current_session_id}, {"_id": 0}))
    if docs:
        return jsonify({
            "status": "success",
            "data": docs,
        })
    else:
        return jsonify({
            "status": "error",
            "message": "无记录",
            "session_id": current_session_id
        }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8700, debug=True)
