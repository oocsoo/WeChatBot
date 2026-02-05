import http.client
import json
from env_loader import TOKEN


def send_text_message(wxid, text):
    """
    发送文本消息！
    :param wxid: 发给谁wx_id!
    :param text: 文本消息内容！
    :return:
    """
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "toWxid": wxid,
       "content": text
    })
    headers = {
       'AUTHORIZATION': TOKEN,
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/sendTextMessage", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))
