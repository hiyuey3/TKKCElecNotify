from config import *
import requests
def sendMsg(msg):

    PushAPI = f'https://push.xyw.cx/'
    WCendPoint = f'/weixin.php'
    requests.post('https://push.xyw.cx/weixin.php',data={'msg':msg,'openid':openid})
