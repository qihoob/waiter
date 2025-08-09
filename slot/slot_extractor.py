# E:\work\waiter\slot\slot_extractor.py
from fuzzywuzzy import process
import re
from prompt_builder.config import SLOT_DICT
from dict.ltp_tokenizer import get_tokenizer

def extract_slots(text: str, threshold=80, tokenizer=None, is_tokenized=False) -> dict:
    """
    从文本中提取槽位信息

    Args:
        text: 输入文本
        tokenizer: 可选的外部分词器
        is_tokenized: 表示输入是否已分词

    Returns:
        dict: 提取到的槽位字典
    """
    slots = {}

    # 获取分词器并进行分词处理
    if not is_tokenized:
        tokenizer = tokenizer or get_tokenizer()
        tokenized_text = tokenizer.tokenize(text)
    else:
        tokenized_text = text

    # 1. 数字型槽位提取
    slots.update(extract_numeric_slots(tokenized_text))

    # 2. 精确关键词匹配
    for slot_name, keywords in SLOT_DICT.items():

        # 精确匹配（基于分词后的结果）
        matched = next((keyword for keyword in keywords if keyword in tokenized_text), None)

        # 若未匹配，尝试模糊匹配
        if not matched:
            try:
                matched, score = process.extractOne(tokenized_text, keywords)
                if score < threshold:
                    continue
            except Exception:
                # 如果 fuzzywuzzy 处理出错，跳过该槽位
                continue

        # 设置槽位值
        if slot_name in ["忌口", "过敏原"]:
            slots.setdefault(slot_name, []).append(matched)
        else:
            slots[slot_name] = matched

    return slots

def extract_numeric_slots(text):
    """统一提取数字型槽位"""
    numeric_slots = {}

    # 提取人数 - 扩展支持多种表达方式
    MIN_PERSONS = 1
    MAX_PERSONS = 20

    # 匹配格式如"1份"、"4人"、"4个人"、"4位"等
    # 增强版正则表达式，处理更多情况
    person_patterns = [
        r'(\d+)个?[人位份餐](?:.{0,3}(?:聚餐|用餐|吃饭|订餐))?',  # 匹配"4人聚餐"等
        r'(?:需要|想要|来|要|点|订)(\d+)个?[人位份餐]',  # 匹配"要4份"等
        r'(\d+)个?[人位份餐](?:的)',  # 匹配"4人的"
    ]

    for pattern in person_patterns:
        person_match = re.search(pattern, text)
        if person_match:
            count = int(person_match.group(1))
            if MIN_PERSONS <= count <= MAX_PERSONS:
                numeric_slots["人数"] = count
                break  # 找到第一个匹配就停止

    # 提取预算
    budget_match = re.search(r'(\d{2,4})元', text)
    if budget_match:
        numeric_slots["预算"] = int(budget_match.group(1))

    return numeric_slots

if __name__ == '__main__':
    # 测试槽位提取
    sample_text = "我想要一个预算在200元以内的餐厅，适合4个人，忌口辣椒和花生"
    extracted_slots = extract_slots(sample_text, tokenizer=None, is_tokenized=False)
    print("提取到的槽位信息:", extracted_slots)

    # 测试数字型槽位提取
    numeric_text = "请帮我找一个适合2个人的餐厅，预算在300元以内"
    numeric_slots = extract_numeric_slots(numeric_text)
    print("提取到的数字型槽位信息:", numeric_slots)

    # 初始化 LTP 分词器
    tokenizer = get_tokenizer()
    # 测试文本
    text = "我想要1份牛排"
    # 提取槽位（自动调用 LTP 分词）
    slots = extract_slots(text, tokenizer=tokenizer)
    print(f"输入: {text}")
    print(f"提取结果: {slots}")

    test_cases = [
        "两杯咖啡",
        "三个人的套餐",
        "4位客人用餐",
        "五份披萨",
        "我要六瓶啤酒",
        "需要八盘凉菜",
        "九碗米饭",
        "我想要1份牛排",
        "来两份炒饭",
        "一个人吃饭",
        "三个人聚餐",
        "需要5份盒饭"
    ]

    print("\n详细测试结果:")
    for text in test_cases:
        slots = extract_slots(text)
        people_count = slots.get("人数", "未提取到")
        print(f"输入: '{text}' -> 人数: {people_count}")
