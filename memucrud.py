
import asyncio
from typing import Dict, List, Any
from env_loader import SILICON_FLOW_API_KEY, LLM_BASE_URL, CHAT_MODEL, EMBEDDING_BASE_URL, EMBED_MODEL, POSTGRES_DSN
from memu.app import MemoryService


class MemuCrud:
    def __init__(self, api_key: str):
        """初始化 MemoryService"""
        self.service = MemoryService(
            # LLM 大模型参数配置
            llm_profiles={
                "default": {
                    "base_url": LLM_BASE_URL,
                    "api_key": api_key,
                    "chat_model": CHAT_MODEL,
                    "client_backend": "sdk"
                },
                "embedding": {
                    "base_url": EMBEDDING_BASE_URL,
                    "api_key": api_key,
                    "embed_model": EMBED_MODEL
                }
            },
            # PostgreSQL 数据库配置（Docker 容器，端口 5433）
            database_config={
                "metadata_store": {
                    "provider": "postgres",
                    "dsn": POSTGRES_DSN
                }
            },
            # 记忆类别配置
            memorize_config={
                "memory_categories": [
                    {"name": "event", "description": "微信聊天记录信息"},
                ]
            },
        )
        # 存储创建的记忆项 ID
        self.created_items = []

    async def create(self, content) -> List[str]:
        """
        创建（Create）操作
        """
        # 创建多个不同类型的记忆项
        memories_to_create = [
            {
                "memory_type": "event",
                "memory_content": content,
                "memory_categories": ["event"],
            }
        ]

        created_ids = []
        for idx, memory_data in enumerate(memories_to_create, 1):
            try:
                result = await self.service.create_memory_item(**memory_data)
                item_id = result.get("memory_item", {}).get("id")
                created_ids.append(item_id)
            except Exception as e:
                print(f"记忆项 {idx} 创建失败: {e}")

        self.created_items = created_ids
        return created_ids[0]

    async def read(self):
        """
        读取（Read）操作
        """
        # 读取所有记忆项！
        try:
            # 使用 list_memory_items 获取所有项
            all_items_result = await self.service.list_memory_items()
            all_items = all_items_result.get('items', [])
            return all_items
        except Exception as e:
            print(f"读取失败: {e}")


# async def main():
#     """主函数 - 运行所有 CRUD 演示"""
#     # 创建演示实例
#     memory = MemuCrud(SILICON_FLOW_API_KEY)
#     try:
#         # 1. 创建记忆项！
#         created_ids = await memory.create('我爱我的国')
#         print(created_ids)
#
#         # 2. 读取记忆项！
#         reade_memory = await memory.read()
#         print(reade_memory)
#     except Exception as e:
#         print(f"发生错误: {e}")
#         import traceback
#         traceback.print_exc()
#
# if __name__ == "__main__":
#     asyncio.run(main())
