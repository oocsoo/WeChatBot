
import http.client
import json
from env_loader import TOKEN
import urllib.request


def get_voice_url(message, sin):
    """
    :param message: 语音消息回调！
    :param sin: 判断私信还是群聊！
    :return :{'ret': 200, 'msg': '操作成功', 'data': {'fileUrl': 'http://wxapii.oos-hazz.ctyunapi.cn/20260122/wx_E2k7qPKTJt8zMpNyLrrX2/2d45e006-0fa0-4b4e-b72d-1c4e4604ffe3.silk?AWSAccessKeyId=9e882e7187c38b431303&Expires=1769662934&Signature=zUQlH2M5HWITtRRP4XOmFL%2FjP9E%3D'}}

    """
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
        "msgId": message.get('Data', {}).get('MsgId', ''),
        "xml": message.get('Data', {}).get('Content', '').get('string', '') if sin == 1 else message.get('Data', {}).get('Content', '').get('string', '').split(":")[-1].strip()
    })
    headers = {
        'AUTHORIZATION': TOKEN,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/downloadVoice", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


def get_voice_silk(msg, sin):
    json_url = get_voice_url(msg, sin)
    file_url = json_url['data']['fileUrl']
    urllib.request.urlretrieve(file_url, './voice/auto.silk')
