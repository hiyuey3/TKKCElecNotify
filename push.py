from config import *
import requests
def SendMsg(msg):
    # PushAPI = f'https://push.余越.我爱你/'
    # WCendPoint = f'/weixin.php'
    requests.post('https://push.xyw.cx/weixin.php',data={'msg':msg,'openid':openid})
