import asyncio
import websockets
import json
import logging
import time
from env_loader import ROBOT_ID, SERVER_IP, SERVER_PORT
from schedule import schedule

# --- 基本配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- WebSocket 连接配置 ---
WEBSOCKET_URI = f"ws://{SERVER_IP}:{SERVER_PORT}/ws"

# 心跳配置，建议60秒发送一次心跳！
HEARTBEAT_INTERVAL = 60


async def send_heartbeat(websocket):
    """
    定期发送心跳包
    """
    while True:
        try:
            heartbeat_msg = {
                "type": "heartbeat",
                "robotid": ROBOT_ID,
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(heartbeat_msg))
            logging.debug("心跳包已发送")
            await asyncio.sleep(HEARTBEAT_INTERVAL)
        except Exception as e:
            logging.error(f"发送心跳失败: {e}")
            break


async def receive_messages():
    """
    连接到 WebSocket 服务器并持续接收回调消息!
    """
    # 无限循环，确保在断开连接后能自动重连
    reconnect_delay = 5  # 初始重连延迟
    max_reconnect_delay = 60  # 最大重连延迟

    while True:
        try:
            # 尝试连接到 WebSocket 服务器
            async with websockets.connect(
                    WEBSOCKET_URI,
                    ping_interval=20,  # 20秒发送一次ping
                    ping_timeout=10,  # 10秒内没收到pong认为连接断开
                    close_timeout=10  # 关闭超时
            ) as websocket:
                logging.info(f"成功连接到 WebSocket 服务器: {WEBSOCKET_URI}")
                # 重置重连延迟
                reconnect_delay = 5

                # 连接后立即发送robotid进行注册
                register_msg = json.dumps({"robotid": ROBOT_ID})
                await websocket.send(register_msg)
                logging.info(f"已向服务器注册robotid: {ROBOT_ID}")

                # 启动心跳任务
                heartbeat_task = asyncio.create_task(send_heartbeat(websocket))

                # 持续监听来自服务器的消息
                async for message in websocket:
                    try:
                        # 尝试将消息解析为JSON格式
                        message_data = json.loads(message)

                        # 处理连接确认消息
                        if message_data.get('type') == 'connection_ack':
                            logging.info(f"连接确认: {message_data.get('message')}")
                            continue

                        # 处理心跳回复
                        if message_data.get('type') == 'heartbeat_reply':
                            logging.debug(f"收到心跳回复: {message_data.get('timestamp')}")
                            continue

                        # 打印普通消息
                        logging.info("--- 收到新的消息 ---")
                        pretty_message = json.dumps(message_data, indent=4, ensure_ascii=False)
                        # print(pretty_message)

                        #################################################################
                        # 在这里可以添加您自己的过滤和处理逻辑！
                        try:
                            await schedule(pretty_message, 0)
                        except Exception as e:
                            logging.error(f"处理消息时发生错误: {e}")
                            logging.debug(f"错误消息内容: {pretty_message}")
                        #################################################################

                    except json.JSONDecodeError:
                        # 如果消息不是有效的JSON，则直接打印原始字符串
                        logging.warning("收到的消息不是有效的JSON格式，打印原始消息:")
                        print(message)

                    logging.info("--- 消息处理完毕 ---\n")

                # 连接断开，取消心跳任务
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

        except (websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.ConnectionClosedOK) as e:
            logging.error(f"连接断开: {e}。将在{reconnect_delay}秒后尝试重新连接...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)

        except ConnectionRefusedError as e:
            logging.error(f"连接被拒绝: {e}。将在{reconnect_delay}秒后尝试重新连接...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)

        except Exception as e:
            logging.error(f"发生未知错误: {e}。将在{reconnect_delay}秒后尝试重新连接...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)


# --- 主程序入口 ---
if __name__ == "__main__":
    logging.info("启动 WebSocket 客户端...")
    try:
        # 运行异步事件循环
        asyncio.run(receive_messages())
    except KeyboardInterrupt:
        logging.info("客户端已手动停止。")