
def get_chat_content(all_items, item_id):
    item = next((i for i in all_items if i.get('id') == item_id), None)
    if item:
        return item.get('summary')
    else:
        print(f"未找到 ID 为 {item_id} 的记忆项")