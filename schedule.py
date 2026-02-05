import json
import os.path
from env_loader import ROBOT_ID, NONE_RESP_NICK_NAME, WELCOME, SILICON_FLOW_API_KEY
import os
import ast
from memucrud import MemuCrud
from get_chatcontent import get_chat_content
from typing import List, Dict
import asyncio

# 全局文件锁，用于保护record.json的并发访问
record_lock = asyncio.Lock()


async def read_chat_record() -> Dict[str, List[Dict[str, str]]]:
    """
    安全地读取record.json文件
    :return: 聊天记录字典
    """
    async with record_lock:
        if os.path.exists('record/record.json'):
            with open('record/record.json', 'r', encoding='utf8') as f:
                return json.load(f)
        else:
            # 确保目录存在
            os.makedirs('record', exist_ok=True)
            # 创建空文件
            with open('record/record.json', 'w', encoding='utf8') as f:
                json.dump({}, f)
            return {}


async def save_chat_record(chat_record: Dict[str, List[Dict[str, str]]]):
    """
    安全地保存record.json文件
    :param chat_record: 聊天记录字典
    """
    async with record_lock:
        # 确保目录存在
        os.makedirs('record', exist_ok=True)
        with open('record/record.json', 'w', encoding='utf8') as f:
            json.dump(chat_record, f, ensure_ascii=False, indent=2)


async def schedule(message, sing_nal):
    """
    接口调度
    :param message: 消息
    :param sing_nal: 信号
    :return:
    """
    # 接收等待处置的消息！
    message_data = json.loads(message)

    # 验证消息格式，确保必要字段存在
    if 'Data' not in message_data:
        print(f"消息缺少 Data 字段，跳过处理: {message_data}")
        return

    if 'FromUserName' not in message_data['Data']:
        print(f"消息缺少 FromUserName 字段，跳过处理: {message_data}")
        return

    # 检查 FromUserName 是否包含 string 字段
    from_user = message_data['Data']['FromUserName']
    if not isinstance(from_user, dict) or 'string' not in from_user:
        print(f"FromUserName 格式不正确，跳过处理: {from_user}")
        return

    from_user_name = from_user['string']

    # 初始化对象存储-桶！
    # if not os.path.exists('data/bucket.json'):
    #     from action.procedure.create_bucket import create_cb
    #     # 创建桶并设置生命周期
    #     create_cb(message_data['RobotId'], "private")
    #     with open('data/bucket.json', 'w') as f:
    #         f.write(json.dumps({message_data['RobotId']: "private"}))

    # 手动回复
    if sing_nal == 1:
        return

    # 自动回复
    if sing_nal == 0:

        # 初始化知识库！
        if message_data["Data"]["Content"]["string"] == '初始化' and message_data["Data"]["ToUserName"]["string"] == "filehelper":

            # 知识库向量入库！
            from RAG.emb_save_db import process_and_save

            # 列出knowledge下所有文件！
            filelist = os.listdir('RAG/knowledge')

            # 循环向量入库！
            for item in filelist:
                result = await process_and_save("RAG/knowledge/%s" % item)
                if result == "success":
                    from action.solo.sendtextmessage import send_text_message
                    send_text_message(
                        "filehelper",
                        "%s 文档向量化入库成功！" % item
                    )
                else:
                    from action.solo.sendtextmessage import send_text_message
                    send_text_message(
                        "filehelper",
                        "%s 文档向量化入库失败！" % item
                    )

        # 判断为好友添加信息
        if from_user_name == "fmessage" and message_data['Data']['MsgType'] == 37:
            from action.solo.agreeaddfriends import agree_friends
            from action.solo.sendtextmessage import send_text_message
            from action.solo.sendimagemessage import send_image_message

            # 自动通过好友！
            result = agree_friends(message_data, '你好！')

            # 自动进行打招呼！
            for i in range(len(ast.literal_eval(WELCOME))):
                send_text_message(result.get("data", {}).get("wxid", ""), ast.literal_eval(WELCOME)[i])

        # 判断消息非自己发送！被动进行回复！
        if from_user_name != ROBOT_ID:

            # 私聊>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>逻辑
            if '@chatroom' not in from_user_name:

                # 私聊文本事件！
                if message_data["Data"]["MsgType"] == 1:

                    # 实例化memu！
                    memory = MemuCrud(SILICON_FLOW_API_KEY)
                    reade_memory = await memory.read()

                    # 从record.json文件中查询聊天记录信息！
                    chat_record = await read_chat_record()
                    record_list = chat_record.get(message_data["Data"]["FromUserName"]["string"], [])

                    if record_list is not None:
                        # 将聊天记录转成gemini所需的聊天记录格式！
                        memory_list: List[str] = []
                        for item in record_list:
                            if item.get('user', '') in str(reade_memory):
                                chat = get_chat_content(reade_memory, item.get('user', ''))
                                memory_list.append('user\n%s' % chat)
                            if item.get('assistant', '') in str(reade_memory):
                                chat = get_chat_content(reade_memory, item.get('assistant', ''))
                                memory_list.append('assistant\n%s' % chat)

                        memory_str = '\n'.join(memory_list)
                    else:
                        memory_str = '\n'

                    # 调用模型进行消息回复！
                    from modelapi.llm_handler import llm_client
                    response = await llm_client.generate_response(message_data['Data']['Content']['string'], memory_str)

                    # 模型拒绝回复，这里不回复！
                    if '拒绝' in response and len(response) <= 5:

                        # 将用户消息，写入到数据库中！
                        user_created_id = await memory.create(message_data['Data']['Content']['string'])
                        assistant_created_id = ''

                        # 判断用户是否在record.json文件中，在就追加，不再就写入！
                        if message_data["Data"]["FromUserName"]["string"] in chat_record:
                            # 将id更新到record.json文件中！
                            chat_record[message_data["Data"]["FromUserName"]["string"]].append({
                                "user": user_created_id,
                                "assistant": assistant_created_id
                            })
                        else:
                            chat_record[message_data["Data"]["FromUserName"]["string"]] = [
                                {
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                }
                            ]

                        # 保存数据到record.json中
                        await save_chat_record(chat_record)
                        return

                    else:
                        # 将用户消息和模型回复的消息，写入到数据库中！
                        user_created_id = await memory.create(message_data['Data']['Content']['string'])
                        assistant_created_id = await memory.create(response)

                        # 判断用户是否在record.json文件中，在就追加，不再就写入！
                        if message_data["Data"]["FromUserName"]["string"] in chat_record:
                            # 将id更新到record.json文件中！
                            chat_record[message_data["Data"]["FromUserName"]["string"]].append({
                                "user": user_created_id,
                                "assistant": assistant_created_id
                            })
                        else:
                            chat_record[message_data["Data"]["FromUserName"]["string"]] = [
                                {
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                }
                            ]

                        # 保存数据到record.json中
                        await save_chat_record(chat_record)

                        # 将模型回复的消息，回复给用户！
                        from action.solo.sendtextmessage import send_text_message
                        send_text_message(
                            from_user_name,
                            response
                        )

                # 私聊图片事件
                if message_data["Data"]["MsgType"] == 3:
                    return

                # 私聊语音消息事件
                if message_data["Data"]["MsgType"] == 34:
                    from action.solo.downloadvoicemessage import get_voice_silk
                    from tencentapi.tencentvoicetext import voice_to_word

                    # 获取音频文件！
                    get_voice_silk(message_data, 1)

                    # 调用一句话识别！
                    voice_result = json.loads(voice_to_word('voice/auto.silk'))
                    voice_text = voice_result.get("Result", "")

                    # 实例化memu！
                    memory = MemuCrud(SILICON_FLOW_API_KEY)
                    reade_memory = await memory.read()

                    # 从record.json文件中查询聊天记录信息！
                    chat_record = await read_chat_record()
                    record_list = chat_record.get(message_data["Data"]["FromUserName"]["string"], [])

                    if record_list is not None:
                        # 将聊天记录转成gemini所需的聊天记录格式！
                        memory_list: List[str] = []
                        for item in record_list:
                            if item.get('user', '') in str(reade_memory):
                                chat = get_chat_content(reade_memory, item.get('user', ''))
                                memory_list.append('user\n%s' % chat)
                            if item.get('assistant', '') in str(reade_memory):
                                chat = get_chat_content(reade_memory, item.get('assistant', ''))
                                memory_list.append('assistant\n%s' % chat)

                        memory_str = '\n'.join(memory_list)
                    else:
                        memory_str = '\n'

                    # 调用模型进行消息回复！
                    from modelapi.llm_handler import llm_client
                    response = await llm_client.generate_response(voice_text, memory_str)

                    # 模型拒绝回复，这里不回复！
                    if '拒绝' in response and len(response) <= 5:

                        # 将用户消息，写入到数据库中！
                        user_created_id = await memory.create(voice_text)
                        assistant_created_id = ''

                        # 判断用户是否在record.json文件中，在就追加，不再就写入！
                        if message_data["Data"]["FromUserName"]["string"] in chat_record:
                            # 将id更新到record.json文件中！
                            chat_record[message_data["Data"]["FromUserName"]["string"]].append({
                                "user": user_created_id,
                                "assistant": assistant_created_id
                            })
                        else:
                            chat_record[message_data["Data"]["FromUserName"]["string"]] = [
                                {
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                }
                            ]

                        # 保存数据到record.json中
                        await save_chat_record(chat_record)
                        return

                    else:
                        # 将用户消息和模型回复的消息，写入到数据库中！
                        user_created_id = await memory.create(voice_text)
                        assistant_created_id = await memory.create(response)

                        # 判断用户是否在record.json文件中，在就追加，不再就写入！
                        if message_data["Data"]["FromUserName"]["string"] in chat_record:
                            # 将id更新到record.json文件中！
                            chat_record[message_data["Data"]["FromUserName"]["string"]].append({
                                "user": user_created_id,
                                "assistant": assistant_created_id
                            })
                        else:
                            chat_record[message_data["Data"]["FromUserName"]["string"]] = [
                                {
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                }
                            ]

                        # 保存数据到record.json中
                        await save_chat_record(chat_record)

                        # 将模型回复的消息，回复给用户！
                        from action.solo.sendtextmessage import send_text_message
                        send_text_message(
                            from_user_name,
                            response
                        )

                # 私聊视频事件
                if message_data["Data"]["MsgType"] == 43:
                    return

            # 群聊>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>逻辑
            if '@chatroom' in from_user_name:

                # 群聊文本消息事件
                if message_data["Data"]["MsgType"] == 1:

                    # 判断是否再不回复列表中。
                    nick_name = message_data.get('Data', {}).get("PushContent", "").split(':')[0].strip()
                    if nick_name not in ast.literal_eval(NONE_RESP_NICK_NAME):
                        # 提取群聊消息内容（格式：wxid:\n消息内容）
                        content_string = message_data["Data"]["Content"]["string"]
                        if ":\n" in content_string:
                            group_message_text = content_string.split(":\n", 1)[1]
                        else:
                            group_message_text = content_string

                        # 实例化memu！
                        memory = MemuCrud(SILICON_FLOW_API_KEY)
                        reade_memory = await memory.read()

                        # 从record.json文件中查询聊天记录信息！
                        chat_record = await read_chat_record()
                        record_list = chat_record.get(message_data["Data"]["FromUserName"]["string"], [])

                        if record_list is not None:
                            # 将聊天记录转成gemini所需的聊天记录格式！
                            memory_list: List[str] = []
                            for item in record_list:
                                if item.get('user', '') in str(reade_memory):
                                    chat = get_chat_content(reade_memory, item.get('user', ''))
                                    memory_list.append('user\n%s' % chat)
                                if item.get('assistant', '') in str(reade_memory):
                                    chat = get_chat_content(reade_memory, item.get('assistant', ''))
                                    memory_list.append('assistant\n%s' % chat)

                            memory_str = '\n'.join(memory_list)
                        else:
                            memory_str = '\n'

                        # 调用模型进行消息回复！
                        from modelapi.llm_handler import llm_client
                        response = await llm_client.generate_response(group_message_text, memory_str)

                        # 模型拒绝回复，这里不回复！
                        if '拒绝' in response and len(response) <= 5:

                            # 将用户消息，写入到数据库中！
                            user_created_id = await memory.create(group_message_text)
                            assistant_created_id = ''

                            # 判断用户是否在record.json文件中，在就追加，不再就写入！
                            if message_data["Data"]["FromUserName"]["string"] in chat_record:
                                # 将id更新到record.json文件中！
                                chat_record[message_data["Data"]["FromUserName"]["string"]].append({
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                })
                            else:
                                chat_record[message_data["Data"]["FromUserName"]["string"]] = [
                                    {
                                        "user": user_created_id,
                                        "assistant": assistant_created_id
                                    }
                                ]

                            # 保存数据到record.json中
                            await save_chat_record(chat_record)
                            return

                        else:
                            # 将用户消息和模型回复的消息，写入到数据库中！
                            user_created_id = await memory.create(group_message_text)
                            assistant_created_id = await memory.create(response)

                            # 判断用户是否在record.json文件中，在就追加，不再就写入！
                            group_who_wx_id = message_data["Data"]["Content"]["string"].split(':')[0].strip()
                            if group_who_wx_id in chat_record:
                                # 将id更新到record.json文件中！
                                chat_record[group_who_wx_id].append({
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                })
                            else:
                                chat_record[group_who_wx_id] = [
                                    {
                                        "user": user_created_id,
                                        "assistant": assistant_created_id
                                    }
                                ]

                            # 保存数据到record.json中
                            await save_chat_record(chat_record)

                            # 将模型回复的消息，回复给用户！
                            from action.solo.sendtextmessage import send_text_message
                            send_text_message(
                                from_user_name,
                                response
                            )

                # 群聊图片事件
                if message_data["Data"]["MsgType"] == 3:
                    return

                # 群聊语音消息事件
                if message_data["Data"]["MsgType"] == 34:

                    # 判断是否再不回复列表中！
                    nickname = message_data.get('Data', {}).get("PushContent", "")

                    if all(item not in nickname for item in ast.literal_eval(NONE_RESP_NICK_NAME)):

                        from action.solo.downloadvoicemessage import get_voice_silk
                        from tencentapi.tencentvoicetext import voice_to_word

                        # 获取音频文件！
                        get_voice_silk(message_data, 0)

                        # 调用一句话识别！
                        voice_result = json.loads(voice_to_word('voice/auto.silk'))
                        voice_text = voice_result.get("Result", "")

                        # 实例化memu！
                        memory = MemuCrud(SILICON_FLOW_API_KEY)
                        reade_memory = await memory.read()

                        # 从record.json文件中查询聊天记录信息！
                        chat_record = await read_chat_record()
                        record_list = chat_record.get(message_data["Data"]["FromUserName"]["string"], [])

                        if record_list is not None:
                            # 将聊天记录转成gemini所需的聊天记录格式！
                            memory_list: List[str] = []
                            for item in record_list:
                                if item.get('user', '') in str(reade_memory):
                                    chat = get_chat_content(reade_memory, item.get('user', ''))
                                    memory_list.append('user\n%s' % chat)
                                if item.get('assistant', '') in str(reade_memory):
                                    chat = get_chat_content(reade_memory, item.get('assistant', ''))
                                    memory_list.append('assistant\n%s' % chat)

                            memory_str = '\n'.join(memory_list)
                        else:
                            memory_str = '\n'

                        # 调用模型进行消息回复！
                        from modelapi.llm_handler import llm_client
                        response = await llm_client.generate_response(voice_text, memory_str)

                        # 模型拒绝回复，这里不回复！
                        if '拒绝' in response and len(response) <= 5:

                            # 将用户消息，写入到数据库中！
                            user_created_id = await memory.create(voice_text)
                            assistant_created_id = ''

                            # 判断用户是否在record.json文件中，在就追加，不再就写入！
                            if message_data["Data"]["FromUserName"]["string"] in chat_record:
                                # 将id更新到record.json文件中！
                                chat_record[message_data["Data"]["FromUserName"]["string"]].append({
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                })
                            else:
                                chat_record[message_data["Data"]["FromUserName"]["string"]] = [
                                    {
                                        "user": user_created_id,
                                        "assistant": assistant_created_id
                                    }
                                ]

                            # 保存数据到record.json中
                            await save_chat_record(chat_record)
                            return

                        else:
                            # 将用户消息和模型回复的消息，写入到数据库中！
                            user_created_id = await memory.create(voice_text)
                            assistant_created_id = await memory.create(response)

                            # 判断用户是否在record.json文件中，在就追加，不再就写入！
                            group_who_wx_id = message_data["Data"]["Content"]["string"].split(':')[0].strip()
                            if group_who_wx_id in chat_record:
                                # 将id更新到record.json文件中！
                                chat_record[group_who_wx_id].append({
                                    "user": user_created_id,
                                    "assistant": assistant_created_id
                                })
                            else:
                                chat_record[group_who_wx_id] = [
                                    {
                                        "user": user_created_id,
                                        "assistant": assistant_created_id
                                    }
                                ]

                            # 保存数据到record.json中
                            await save_chat_record(chat_record)

                            # 将模型回复的消息，回复给用户！
                            from action.solo.sendtextmessage import send_text_message
                            send_text_message(
                                from_user_name,
                                response
                            )

                # 群聊视频事件
                if message_data["Data"]["MsgType"] == 43:
                    return
