import http.client
import json
from env_loader import TOKEN


def cards(towxid, nickname, targetwxid):
    """
    发送名片
    :param towxid:
    :param nickname:
    :param targetwxid:
    :return:
    """
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "toWxid": towxid,
       "nickName": nickname,
       "nameCardWxid": targetwxid
    })
    headers = {
       'AUTHORIZATION': TOKEN,
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/sendCardMessage", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


# 调用方法
# result = cards('45076751641@chatroom', '马先宏', 'wxid_cnw193tl86kx22')
# print(result)
