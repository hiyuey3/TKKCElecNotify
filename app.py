# encoding=utf-8
from flask import Flask, request, jsonify, Blueprint, redirect, render_template
import eUtil
import hashlib
import requests
import pymongo
import flask

client = pymongo.MongoClient("mongodb://localhost:27017")
main_db = client["main_db"]
mdb_session = main_db["sessions"]
mdb_records = main_db["records"]
app = Flask(__name__)
# WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "your_wechat_token")  # 请替换成你的微信 Token
WECHAT_APP_ID = "wx2923721f21fef02d"
WECHAT_APP_SECRET = "0260b34707815bed26e753af552b7644"
WECHAT_TOKEN = 'token_sasosnoibjkdbhc'
WECHAT_REDIRECT_URI = 'http://api2.5i03.cn/WeiXin/auth'


@app.route('/api/eLogin', methods=['POST'])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    session_data = eUtil.eGetSession(username)
    if not session_data:
        new_session = eUtil.eLogin(username, password)
        if new_session:
            new_session_id = eUtil.eGenSession_id()
            eUtil.eSaveSession(username, new_session, password, new_session_id)
            session_data = {"e_session": new_session, "e_session_id": new_session_id}
        else:
            return jsonify({"status": "error", "message": "登录失败"}), 401

    return jsonify({
        "status": "success",
        "message": "登录成功",
        "e_session_id": session_data["e_session_id"]
    })


@app.route('/api/eQuery', methods=['POST', 'GET'])
def api_query():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"status": "error", "message": "缺少 username 参数"}), 400

    session_data = eUtil.eGetSession(username)
    if not session_data:
        return jsonify({"status": "error", "message": "会话无效或未登录"}), 401

    current_session_id = session_data["e_session_id"]
    docs = list(eUtil.mdb_records.find({"username": username, "e_session_id": current_session_id}, {"_id": 0}))
    if not docs:
        res_text = eUtil.eFetchData(username)
        if res_text:
            eUtil.HTMLparser(res_text, username, current_session_id)
            docs = list(eUtil.mdb_records.find({"username": username, "e_session_id": current_session_id}, {"_id": 0}))

    return jsonify({"status": "success", "data": docs}) if docs else jsonify(
        {"status": "error", "message": "无记录"}), 404


@app.route('/Check', methods=['GET'])
def wc_check():
    if request.method == "GET":
        signature = request.args.get("signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        echostr = request.args.get("echostr")

        if not all([signature, timestamp, nonce, echostr]):
            return jsonify({"status": "error", "message": "缺少参数"}), 400

        token_list = sorted([WECHAT_TOKEN, timestamp, nonce])
        hashcode = hashlib.sha1("".join(token_list).encode()).hexdigest()

        if hashcode == signature:
            return echostr
        else:
            return jsonify({"status": "error", "message": "签名校验失败"}), 403

    return jsonify({"status": "error", "message": "无效请求"}), 405
    # data = request.json


# @app.route("/WeiXin",methods=['GET'])
# def wc_login():
#     code=request.args.get('code')
#     if not code:
#         return jsonify({"status": "error", "message": "<UNK>"}), 400
#     else:
#         wc_auth_s2=requests.post("https://api.weixin.qq.com/sns/oauth2/access_token?appid="+appid+"&secret="+appsecert+"&code="+code+"&grant_type=authorization_code").text
#         return wc_auth_s2
#         # mdb_session.insert_one(wc_auth_s2,upsert=True)
#             # save_openid=mdb_session.update_one("")
#
#         # return jsonify({"status": "success", "code": code}),200

@app.route('/about')
def about_me():
    return render_template('about.html')


@app.route('/WeiXin')
def index():
    return '<a href="/WeiXin/login">Login with WeChat</a>'


@app.route('/WeiXin/login')
def login():
    wechat_url = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={WECHAT_APP_ID}&redirect_uri={WECHAT_REDIRECT_URI}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    return redirect(wechat_url)


@app.route('/WeiXin/auth')
def auth():
    code = request.args.get('code')
    if not code:
        return 'Authorization Failed.'
    token_url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}&code={code}&grant_type=authorization_code'
    response = requests.get(token_url)
    data = response.json()
    access_token = data.get('access_token')
    openid = data.get('openid')
    if access_token and openid:
        user_info_url = f'https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN'
        user_response = requests.get(user_info_url)
        # enc_doc_response= user_response.encode('iso-8859-1').decode('utf8')
        user_data = user_response.json()
        # 在这里，你可以将用户信息保存到数据库，并设置 session
        # session['user_info'] = user_data
        # nickname_1=user_data.get("nickname")
        return (f'<img src="{user_data.get("headimgurl")}"></img><br /> Welcome, {user_data.get("nickname").encode("iso-8859-1").decode("utf8")}!<br /><br />{user_data.get("openid")}'
                f'<br />请在下方绑定你的学校账号密码<br />'
                )
    return 'Failed to fetch user info.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
