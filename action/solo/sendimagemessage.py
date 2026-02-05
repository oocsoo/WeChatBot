import http.client
import json
from env_loader import TOKEN


def send_image_message(towxid, imgurl):
    """
    发送图片消息！
    :param towxid: 发给谁wx_id！
    :param imgurl: 在线图片url地址！
    :return:
    """
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "toWxid": towxid,
       "imgUrl": imgurl
    })
    headers = {
       'AUTHORIZATION': TOKEN,
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/sendImageMessage", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


# # 使用方法
# result = send_image_message(
#     'wxid_cnw193tl86kx22',
#     'https://shanghai-9.zos.ctyun.cn/wxid_cnw193tl86kx22/1.jpg?AWSAccessKeyId=24OZWDYSXWXLAXTN5LKW&Signature=gxWrvqrcBHWeYoIGbg2JJU9Vt%2BQ%3D&Expires=1768888601'
#     )
# print(result)
