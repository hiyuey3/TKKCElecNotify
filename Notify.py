import requests;import urllib.parse

def Bark(title: str, message: str, bark_url: str):
    title = urllib.parse.quote(title)
    message = urllib.parse.quote(message)
    url = f"{bark_url}/{title}/{message}"
    r = requests.get(url)
    if r.status_code == 200:
        print("✅ Bark 推送成功")
    else:
        print(f"❌ Bark 推送失败：{r.status_code}")

def SelfWCPush(title: str, message: str, openid: str):
    message=message+'-' * 12 + ('\n这是程序自动生成的。\n校方系统实时数据的更新时间约为1h，\n日用电数据的更新时间为次日。\n'
                 "课程设计只供学习和交流使用，请勿滥用。\n"
                 )
    HtmlMessage = message.replace('\n', '<br>')
    url = f"http://api.5i03.cn/push/weixin.php?openid={openid}&title={title}&msg={HtmlMessage}"
    r=requests.get(url)
    if r.status_code == 200:
        print("✅ WeChat 推送成功")
    else:
        print(f"❌ WeChat 推送失败：{r.status_code}")
