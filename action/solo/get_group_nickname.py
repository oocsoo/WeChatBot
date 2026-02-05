import http.client
import json
from env_loader import TOKEN


def nickname(wx_id):
    """
    通过群id获取群昵称！
    :param wx_id:
    :return: {"ret":200,"msg":"获取联系人信息成功","data":[{"userName":"45076751641@chatroom","nickName":"花花","pyInitial":"HH","quanPin":"huahua","sex":0,"remark":"","remarkPyInitial":null,"remarkQuanPin":null,"signature":null,"alias":null,"snsBgImg":null,"country":null,"bigHeadImgUrl":null,"smallHeadImgUrl":"http://wx.qlogo.cn/mmcrhead/tSuicoXd1h8trAicAiadgr5x91CJfdVosYzicWwC8SvT5iaTQcGDf4P7cGQoQCXhLtc6mibfas4S2jDN0/0","description":null,"cardImgUrl":null,"labelList":null,"province":null,"city":null,"phoneNumList":null}]}
    """
    conn = http.client.HTTPConnection("124.221.45.58")
    payload = json.dumps({
       "wxids": [
          wx_id
       ]
    })
    headers = {
       'AUTHORIZATION': TOKEN,
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/getBriefInfo", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))
