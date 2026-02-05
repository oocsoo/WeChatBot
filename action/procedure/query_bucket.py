
# -*-coding:utf-8 -*
from boto3.session import Session


def query_buckets():
    """
    查询桶列表！
    :return: {'success': True, 'response': {'ResponseMetadata': {'RequestId': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'ct-zos/1.22.1', 'date': 'Thu, 23 Oct 2025 00:48:57 GMT', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'connection': 'keep-alive', 'vary': 'Accept-Encoding', 'x-amz-request-id': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}, 'RetryAttempts': 0}, 'Buckets': [{'Name': 'testing-bucket', 'CreationDate': datetime.datetime(2025, 10, 22, 5, 55, 36, 792000, tzinfo=tzutc())}], 'Owner': {'DisplayName': '马**', 'ID': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}}}
    """
    # 配置项
    access_key = "24OZWDYSXWXLAXTN5LKW"
    secret_key = "n6UTcEnyIfy4cKVFUNnrHCKIDTqGXcnONP40VhkG"
    url = "https://shanghai-9.zos.ctyun.cn"

    # 创建session
    session = Session(access_key, secret_key)
    s3_client = session.client("s3", endpoint_url=url)

    # 发起请求
    response = s3_client.list_buckets()

    # 返回查询到的数据！
    return {
        'success': True,
        'response': response,
    }


# 调用方法
# if __name__ == '__main__':
#     result =query_buckets()
#     print(result)
