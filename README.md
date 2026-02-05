# WeChat Bot - 上下文记忆功能微信客服

基于[wechatbot框架](https://www.wechatbot.online) 和 WebSocket 的智能微信客服，支持 AI 对话、RAG 知识库检索、语音识别等功能。

## 功能特性

- 🤖 **AI 对话**：支持多种大语言模型（DeepSeek、Qwen、KIMI 等）
- 📚 **RAG 知识库**：基于向量数据库的文档检索和问答
- 🎤 **语音识别**：集成腾讯云语音转文字服务
- 💾 **数据持久化**：使用 PostgreSQL + pgvector 存储对话历史
- 🔄 **自动重连**：WebSocket 断线自动重连机制
- 🐳 **Docker 部署**：一键构建和运行

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+

或者本地运行：
- Python 3.13+
- PostgreSQL 数据库（带 pgvector 扩展）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/oocsoo/WeChatBot
cd wechatbot
```

### 2. 配置环境变量

编辑 `.env` 文件，配置必要的参数：

```bash
# 基础配置
ROBOT_ID=your_robot_id          # 机器人微信ID
TOKEN=your_token                # 认证令牌
SERVER_IP=server_ip             # WebSocket 服务器地址
SERVER_PORT=5555                # WebSocket 服务器端口

# AI 模型配置（选择使用的模型配置对应密钥）
DEEPSEEK_API_KEY=sk-xxx         # DeepSeek API 密钥
SILICON_FLOW_API_KEY=sk-xxx     # 硅基流动 API 密钥
CHAT_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct

# 数据库配置
POSTGRES_DSN=postgresql://user:password@host:port/database

# 其他配置
TOP_K=5                         # 知识库检索数量
RERANK_THRESHOLD=0              # 重排阈值
```

### 3. 使用 Docker 部署（推荐）

#### 构建镜像

```bash
docker-compose build
```

#### 启动容器

```bash
docker-compose up -d
```

#### 查看日志

```bash
docker-compose logs -f
```

#### 停止容器

```bash
docker-compose stop
```

#### 重启容器

```bash
docker-compose restart
```

### 4. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 配置说明

### 核心配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `ROBOT_ID` | 机器人微信ID | wxid_xxx |
| `TOKEN` | 认证令牌 | wx_xxx |
| `SERVER_IP` | WebSocket 服务器地址 | 127.0.0.1 |
| `SERVER_PORT` | WebSocket 服务器端口 | 5555 |

### AI 模型配置

支持多种 AI 模型，配置对应的 API 密钥即可：

- **DeepSeek**：`DEEPSEEK_API_KEY`
- **KIMI**：`KIMI_API_KEY`
- **OpenRouter**：`OPEN_ROUTER_API_KEY`
- **硅基流动**：`SILICON_FLOW_API_KEY`

### RAG 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `EMBED_MODEL` | 向量模型 | Qwen/Qwen3-Embedding-8B |
| `RERANK_MODEL` | 重排模型 | Qwen/Qwen3-Reranker-8B |
| `TOP_K` | 检索结果数量 | 5 |
| `RERANK_THRESHOLD` | 重排阈值 | 0 |

### 其他配置

- `WELCOME`：自动通过好友申请后的欢迎语
- `NONE_RESP_NICK_NAME`：群聊中不回复的用户昵称列表

## 目录结构

```
wechatbot/
├── main.py                 # 主程序入口
├── schedule.py             # 消息调度处理
├── env_loader.py           # 环境变量加载
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore           # Docker 构建忽略文件
├── RAG/                    # RAG 知识库文档目录
├── data/                   # 数据存储目录
├── record/                 # 记录文件目录
├── image/                  # 图片文件目录
├── action/                 # 动作处理模块
├── modelapi/               # 模型 API 接口
├── tencentapi/             # 腾讯云 API 接口
└── src/                    # 源代码目录
```

## 使用方法

### 添加 RAG 知识库文档

1. 将文档文件（PDF、Word、Excel 等）放入 `RAG/` 目录
2. 重启容器使文档生效.
3. 在机器人微信的 ***文件传输助手*** 中发送 初始化 三个字后自动父子分块->向量化->入库

```bash
docker-compose restart
```

### 修改配置参数

1. 编辑 `.env` 文件修改配置
2. 重启容器使配置生效：

```bash
docker-compose restart
```

### 查看运行日志

```bash
# 实时查看日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100
```

### 进入容器调试

```bash
docker-compose exec wechatbot bash
```

## Docker 管理

### 重新构建镜像

当修改以下内容时需要重新构建镜像：
- Dockerfile
- requirements.txt
- Python 代码文件

```bash
docker-compose build --no-cache
docker-compose up -d
```

### 不需要重新构建的情况

以下修改只需重启容器：
- 修改 `.env` 配置文件
- 修改 `docker-compose.yml`
- 在 `RAG/`、`data/` 等挂载目录中添加/修改文件

```bash
# 修改 docker-compose.yml 后
docker-compose down
docker-compose up -d

# 修改 .env 或挂载目录文件后
docker-compose restart
```

## 常见问题

### 1. Docker 构建很慢

**问题**：构建镜像时卡在安装依赖步骤

**解决方案**：
- Dockerfile 已配置国内镜像源（清华大学）
- 如果还是慢，可以尝试更换为阿里云镜像源
- 使用 `--progress=plain` 查看详细构建日志

```bash
docker-compose build --progress=plain
```

### 2. 容器启动后立即退出

**问题**：容器无法正常运行

**解决方案**：
1. 查看日志找出错误原因：
```bash
docker-compose logs
```

2. 检查 `.env` 配置是否正确
3. 确认 WebSocket 服务器地址可访问

### 3. 无法连接到 WebSocket 服务器

**问题**：日志显示连接被拒绝

**解决方案**：
1. 检查 `SERVER_IP` 和 `SERVER_PORT` 配置
2. 确认服务器防火墙规则
3. 如果服务器在本地，可以使用 `network_mode: host`

### 4. RAG 文档更新不生效

**问题**：添加新文档后机器人无法识别

**解决方案**：
1. 确认 `RAG/` 目录已在 `docker-compose.yml` 中挂载
2. 重启容器：`docker-compose restart`
3. 检查文档格式是否支持（PDF、Word、Excel）

## 注意事项

⚠️ **安全提醒**：
- `.env` 文件包含敏感信息，请勿提交到版本控制系统
- 建议使用 `.env.example` 作为配置模板
- 生产环境请修改默认密钥和令牌

⚠️ **性能优化**：
- 首次运行会下载向量模型，需要一定时间
- 建议为容器分配足够的内存（至少 2GB）
- 大量文档检索时可能需要更多资源

⚠️ **数据备份**：
- 定期备份 `data/` 目录中的数据
- 定期备份 PostgreSQL 数据库
- 重要对话记录建议异地备份

## 技术栈

- **语言**：Python 3.13
- **框架**：asyncio + websockets
- **AI 模型**：DeepSeek、Qwen、KIMI
- **向量数据库**：ChromaDB + pgvector
- **数据库**：PostgreSQL
- **部署**：Docker + Docker Compose

## 许可证

## 联系方式

[ 作者微信：youeyec ]
