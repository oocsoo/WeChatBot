# env_loader.py
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 环境变量
ROBOT_ID = os.getenv('ROBOT_ID')
TOKEN = os.getenv('TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = os.getenv('SERVER_PORT')
OPEN_ROUTER_API_KEY = os.getenv('OPEN_ROUTER_API_KEY')
SECRET_ID = os.getenv('SECRET_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
WELCOME = os.getenv('WELCOME')
NONE_RESP_NICK_NAME = os.getenv('NONE_RESP_NICK_NAME')
SILICON_FLOW_API_KEY = os.getenv('SILICON_FLOW_API_KEY')
LLM_BASE_URL = os.getenv('LLM_BASE_URL')
CHAT_MODEL = os.getenv('CHAT_MODEL')
EMBEDDING_BASE_URL = os.getenv('EMBEDDING_BASE_URL')
EMBED_MODEL = os.getenv('EMBED_MODEL')
POSTGRES_DSN = os.getenv('POSTGRES_DSN')
TOP_K = os.getenv('TOP_K')
