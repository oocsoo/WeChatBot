import sys
import os
import shutil

def copyFile(src, dst):
    try:
        shutil.copy(src, dst)
    except IOError:
        print(
            "install failed, maybe file not exist,please copy service-2.s3.sdk-extras.json to python install path by yourself")
        print("src path\n" + src + "\ndst path\n" + dst)
    else:
        print("copy \n" + dst + "  complete")

pythonPath=sys.executable
pytopPath=pythonPath[0:pythonPath.rfind("\\")]
dstPath=pytopPath + "\\Lib\\site-packages\\botocore\\data\\s3\\2006-03-01\\service-2.s3.sdk-extras.json"
dstPath1=pytopPath + "\\Lib\\site-packages\\botocore\\data\\s3\\2006-03-01\\service-2.sdk-extras.json"
currentPath=os.getcwd()
sdkExtras=currentPath+"\\service-2.s3.sdk-extras.json"
copyFile(sdkExtras, dstPath)
copyFile(sdkExtras, dstPath1)
