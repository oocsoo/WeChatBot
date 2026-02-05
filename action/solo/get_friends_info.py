import http.client
import json


def get_fiends_wx_id_list(token):
   """
   获取好友微信id列表！
   :return:
   """
   conn = http.client.HTTPConnection("124.221.45.58")
   payload = json.dumps({})
   headers = {
      'AUTHORIZATION': token,
      'Content-Type': 'application/json'
   }
   conn.request("POST", "/fetchContactsList", payload, headers)
   res = conn.getresponse()
   data = res.read()
   return json.loads(data.decode("utf-8"))


def get_friends_wx_details(token):
   """
   获取好像详细信息！
   :param wx_list:
   :return:
   """
   conn = http.client.HTTPConnection("124.221.45.58")
   payload = json.dumps({
      "wxids": get_fiends_wx_id_list(token).get("data").get("friends"),
   })
   headers = {
      'AUTHORIZATION': token,
      'Content-Type': 'application/json'
   }
   conn.request("POST", "/getDetailInfo", payload, headers)
   res = conn.getresponse()
   data = res.read()
   return json.loads(data.decode("utf-8"))

