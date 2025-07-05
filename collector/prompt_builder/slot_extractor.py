import re
from collector.prompt_builder.config import SLOT_DICT
from fuzzywuzzy import process


def extract_slots(text: str, threshold=80) -> dict:
    slots = {}

    # 预处理：插入空格，帮助 jieba 更好切分数字+量词+名词结构
    #text = preprocess_text(text)

    # 1. 数字型槽位提取
    slots.update(extract_numeric_slots(text))

    # 2. 精确关键词匹配
    for slot_name, keywords in SLOT_DICT.items():
        matched = None

        # 精确匹配
        for keyword in keywords:
            if keyword in text:
                matched = keyword
                break

        # 若未匹配，尝试模糊匹配
        if not matched:
            matched, score = process.extractOne(text, keywords)
            if score < threshold:
                continue

        # 设置槽位值
        if slot_name in ["忌口", "过敏原"]:
            slots.setdefault(slot_name, []).append(matched)
        else:
            slots[slot_name] = matched



    return slots


def preprocess_text(text):
    """预处理文本，提高数字+量词模式的识别能力"""
    # 插入空格，强制切分数字+量词+名词结构
    text = re.sub(r'(\d+)([个位元人])', r'\1 \2', text)
    text = re.sub(r'(\d+)([元块])', r'\1 \2', text)
    return text


def extract_numeric_slots(text):
    """统一提取数字型槽位"""
    numeric_slots = {}
    if m := re.search(r'(\d+)个?[人位]', text):
        numeric_slots["人数"] = int(m.group(1))
    if m := re.search(r'(\d{2,4})元', text):
        numeric_slots["预算"] = int(m.group(1))
    return numeric_slots
