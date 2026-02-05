import http.client
import json
import re
from env_loader import TOKEN


def extract_data(content):
    """
    获取v3 v4数据
    :param content:好友回调数据！
    :return: v3/v4
    """
    result = {
        'fromusername': None,
        'encryptusername': None,
        'ticket': None,
        'scene': None
    }
    # 提取encryptusername的值（v3开头）
    encryptusername_pattern = r'encryptusername="(v3_[^"]+)"'
    match = re.search(encryptusername_pattern, content['Data']['Content']['string'])
    if match:
        result['encryptusername'] = match.group(1)

    # 提取ticket的值（v4开头）
    ticket_pattern = r'ticket="(v4_[^"]+)"'
    match = re.search(ticket_pattern, content['Data']['Content']['string'])
    if match:
        result['ticket'] = match.group(1)

    return result


def agree_friends(data, content):
    """
    通过好友添加！
    """
    extracted_data = extract_data(data)
    print('<>'*100)
    print(extracted_data)
    print('<>' * 100)
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "scene": 3,
       "content": content,
       "v3": extracted_data['encryptusername'],
       "v4": extracted_data['ticket'],
       "option": 3
    })
    headers = {
       'AUTHORIZATION': TOKEN,
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/addContacts", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

