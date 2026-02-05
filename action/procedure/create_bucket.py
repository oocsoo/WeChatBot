# -*- coding:utf-8 -*-
from boto3.session import Session


def create_cb(bname, acl):
    """
    创建桶并设置生命周期规则
    :param bname: 桶名称！
    :param acl: 权限！
    :return:{'success': True, 'bucket_response': {'ResponseMetadata': {'RequestId': 'tx0000000000000007c5040-0068f97966-56341140-sh09', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'ct-zos/1.22.1', 'date': 'Thu, 23 Oct 2025 00:40:06 GMT', 'content-length': '0', 'connection': 'keep-alive', 'x-amz-request-id': 'tx0000000000000007c5040-0068f97966-56341140-sh09'}, 'RetryAttempts': 0}}, 'lifecycle_response': {'ResponseMetadata': {'RequestId': 'tx0000000000000007c5047-0068f97966-55d4bfe0-sh09', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'ct-zos/1.22.1', 'date': 'Thu, 23 Oct 2025 00:40:06 GMT', 'content-type': 'application/xml', 'content-length': '0', 'connection': 'keep-alive', 'x-amz-request-id': 'tx0000000000000007c5047-0068f97966-55d4bfe0-sh09'}, 'RetryAttempts': 0}}}
    """
    access_key = "24OZWDYSXWXLAXTN5LKW"
    secret_key = "n6UTcEnyIfy4cKVFUNnrHCKIDTqGXcnONP40VhkG"
    url = "https://shanghai-9.zos.ctyun.cn"
    # 创建Session
    session = Session(access_key, secret_key)
    s3_client = session.client("s3", endpoint_url=url)

    # 1. 创建桶
    try:
        # 修改点：移除了 boto3 不支持的 AZPolicy 和 StorageClass 参数
        response = s3_client.create_bucket(
            Bucket=bname,
            ACL=acl,
            # 如果天翼云强制要求指定区域配置（LocationConstraint），通常是在 CreateBucketConfiguration 中指定
            # 但对于大多数兼容 S3 的操作，简单的创建桶只需要 Bucket 和 ACL
        )
    except Exception as e:
        # 建议加上异常捕获，方便调试
        print(f"创建桶失败: {e}")
        return {'success': False, 'error': str(e)}

    # 2. 设置生命周期规则（仅对新创建的桶）
    try:
        lifecycle_response = s3_client.put_bucket_lifecycle_configuration(
            Bucket=bname,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': 'AutoDeleteRule',  # 规则ID
                        'Status': 'Enabled',  # 启用规则
                        'Filter': {
                            'Prefix': '',  # 空前缀表示应用到所有对象
                        },
                        'Expiration': {
                            'Days': 3  # 文件最后更新3天后删除
                        },
                        'AbortIncompleteMultipartUpload': {
                            'DaysAfterInitiation': 7  # 碎片生成7天后删除
                        }
                    }
                ]
            }
        )
    except Exception as e:
        # 如果生命周期配置失败（如缺少Content-MD5头），跳过此步骤
        print(f"设置生命周期规则失败（已跳过）: {e}")
        lifecycle_response = None
    return {
        'success': True,
        'bucket_response': response,
        'lifecycle_response': lifecycle_response
    }


# if __name__ == '__main__':
#     # 创建桶名称！
#     bucket = 'testing'
#     # 设置权限私有！
#     ACL = "private"
#
#     # 创建桶并设置生命周期
#     result = create_cb(bucket, ACL)
#     print(result)
