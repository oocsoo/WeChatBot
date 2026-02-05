import http.client
import json
from env_loader import TOKEN


def forward_message(to_wx_id, xml):
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "toWxid": to_wx_id,
       "xml": xml
    })
    headers = {
       'AUTHORIZATION': TOKEN,
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/sendForwardImageMessage", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))
