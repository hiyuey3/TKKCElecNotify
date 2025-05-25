from flask import Blueprint, request, redirect
import requests

auth_bp = Blueprint('auth', __name__)

WECHAT_APP_ID = "wx2923721f21fef02d"
WECHAT_APP_SECRET = "0260b34707815bed26e753af552b7644"
WECHAT_REDIRECT_URI = 'http://api2.5i03.cn/WeiXin/auth'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.args.get("way") == "wc":
        wechat_url = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={WECHAT_APP_ID}&redirect_uri={WECHAT_REDIRECT_URI}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
        return redirect(wechat_url)
    elif request.args.get("way") == "qq":
        return '<UNK>'
