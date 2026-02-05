# -*- coding:utf-8 -*-
from boto3.session import Session
import hashlib
import base64


# 上传文件后获取下载地址和微信使用！
def test_po(bname, key, file_path, md5=None):
    """
    上传图片！
    :param bname:
    :param key:
    :param file_path:
    :param md5:
    :return: {'success': True, 'response': {'ResponseMetadata': {'RequestId': 'tx000000000000000a493f2-00693fbf80-5f7f908f-sh09', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'ct-zos/1.22.1', 'date': 'Mon, 15 Dec 2025 07:57:53 GMT', 'content-length': '0', 'connection': 'keep-alive', 'etag': '"930d1eabb83772e6baf061d415f27436"', 'accept-ranges': 'bytes', 'x-amz-request-id': 'tx000000000000000a493f2-00693fbf80-5f7f908f-sh09'}, 'RetryAttempts': 0}, 'ETag': '"930d1eabb83772e6baf061d415f27436"'}, 'download_url': 'https://shanghai-9.zos.ctyun.cn/wxid_o9jco5r4p63l22/9855.jpg?AWSAccessKeyId=24OZWDYSXWXLAXTN5LKW&Signature=B0J6xY%2FK1ZVXKjM%2BXImf34TlBq0%3D&Expires=1766044675', 'file_key': '9855.jpg', 'bucket_name': 'wxid_o9jco5r4p63l22', 'wechat_use': 'https://shanghai-9.zos.ctyun.cn/wxid_o9jco5r4p63l22/9855.jpg'}
    """
    access_key = "24OZWDYSXWXLAXTN5LKW"
    secret_key = "n6UTcEnyIfy4cKVFUNnrHCKIDTqGXcnONP40VhkG"
    url = "https://shanghai-9.zos.ctyun.cn"

    session = Session(access_key, secret_key)
    s3_client = session.client("s3", endpoint_url=url)

    try:
        # 以二进制模式读取文件
        with open(file_path, 'rb') as file:
            file_content = file.read()
            # 计算MD5（如果未提供）
            if md5 is None:
                md5 = hashlib.md5(file_content).digest()
                md5 = base64.b64encode(md5).decode('utf-8')

        # 重新以二进制模式打开文件用于上传
        with open(file_path, 'rb') as file:
            response = s3_client.put_object(
                ACL='private',
                Bucket=bname,
                Metadata={'m1': 'm1'},
                Body=file,  # 直接传递文件对象
                Key=key,
                ContentMD5=md5,
                ServerSideEncryption='AES256',
                Tagging='tag=tag-value'
            )

        # print("✅ 文件上传成功！")
        # print(f"ETag: {response['ETag']}")

        # 生成下载地址（预签名URL）
        download_url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bname,
                    'Key': key
                },
                ExpiresIn=72 * 3600  # 72小时有效期
            )

        return {
            'success': True,
            'response': response,
            'download_url': download_url,
            'file_key': key,
            'bucket_name': bname,
            'wechat_use': '%s/%s/%s' % (url, bname, key)
        }

    except Exception as e:
        print(f"❌ 文件上传失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# # 调用方法！
# bucket = 'wxid_cnw193tl86kx22'
# file_key = '1.jpg'
# file_path = 'C:\\Users\\Administrator.USER-20250215OT\\Desktop\\memorycus\\image\\1.jpg'
# # 发起请求
# result = test_po(bucket, file_key, file_path)
# print(result)


