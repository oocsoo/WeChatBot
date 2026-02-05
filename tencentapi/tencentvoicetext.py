# -*- coding: utf-8 -*-
from env_loader import SECRET_ID, SECRET_KEY
import json
import base64
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


# 接口帮助文档：https://console.cloud.tencent.com/api/explorer?Product=asr&Version=2019-06-14&Action=SentenceRecognition
# SDK接入： https://cloud.tencent.com/document/sdk
def voice_to_word(path_data):
    '''
    将声音文件slik转文字
    :param path_data:
    :return: {"Result": "你好，测试一下声音。", "AudioDuration": 2687, "WordSize": 0, "WordList": null, "RequestId": "40bfbe89-b7c6-487e-9d4d-da319d4d3c7c"}

    '''
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性
        # 以下代码示例仅供参考，建议采用更安全的方式来使用密钥
        # 请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = asr_client.AsrClient(cred, "", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.SentenceRecognitionRequest()
        params = {
            "EngSerViceType": "16k_zh",
            "SourceType": 1,
            "VoiceFormat": "silk",
            "Data": base64.b64encode(open(path_data, "rb").read()).decode('utf-8'),
            "DataLen": 6400
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SentenceRecognitionResponse的实例，与请求对象对应
        resp = client.SentenceRecognition(req)
        # 输出json格式的字符串回包
        return resp.to_json_string()

    except TencentCloudSDKException as err:
        print(err)


# 调用方法
# result = voice_to_word('C:\\Users\\Administrator.USER-20250215OT\\Desktop\\memorycus\\api\\auto.silk')
# print(result)
