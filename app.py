from flask import Flask, request, jsonify
import eUtil
import hashlib
app = Flask(__name__)
# WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "your_wechat_token")  # 请替换成你的微信 Token
WECHAT_TOKEN='api.5i03.cn'

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
            session_data = {"session": new_session, "session_id": new_session_id}
        else:
            return jsonify({"status": "error", "message": "登录失败"}), 401

    return jsonify({
        "status": "success",
        "message": "登录成功",
        "session_id": session_data["session_id"]
    })


@app.route('/api/eQuery', methods=['POST','GET'])
def api_query():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"status": "error", "message": "缺少 username 参数"}), 400

    session_data = eUtil.eGetSession(username)
    if not session_data:
        return jsonify({"status": "error", "message": "会话无效或未登录"}), 401

    current_session_id = session_data["session_id"]
    docs = list(eUtil.records.find({"username": username, "session_id": current_session_id}, {"_id": 0}))
    if not docs:
        res_text = eUtil.eFetchData(username)
        if res_text:
            eUtil.HTMLparser(res_text, username, current_session_id)
            docs = list(eUtil.records.find({"username": username, "session_id": current_session_id}, {"_id": 0}))

    return jsonify({"status": "success", "data": docs}) if docs else jsonify(
        {"status": "error", "message": "无记录"}), 404

@app.route('/api/WC_Check',methods=['GET'])
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
            return echostr  # 返回 `echostr` 让微信服务器确认
        else:
            return jsonify({"status": "error", "message": "签名校验失败"}), 403

    return jsonify({"status": "error", "message": "无效请求"}), 405
    data = request.json



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
