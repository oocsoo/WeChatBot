import http.client
import json
from env_loader import TOKEN


def send_at_text_message(wx_id, at_who, text):
    """
    发送文本消息！
    :param wx_id: 发给谁wx_id!
    :param at_who:
    :param text: 文本消息内容！
    :return:
    """
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "toWxid": wx_id,
       "ats": at_who,
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


# 调用方法
# result = send_at_text_message("45076751641@chatroom", "wxid_cnw193tl86kx22", 'test@message')
# print(result)
