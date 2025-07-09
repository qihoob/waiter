from fuzzywuzzy import process
import re
from prompt_builder.config import SLOT_DICT
from dict.ltp_tokenizer import get_tokenizer

# 定义中文数字到阿拉伯数字的映射
CHINESE_NUMBERS = {
    '零': 0, '一': 1, '二': 2, '两': 2,
    '三': 3, '四': 4, '五': 5, '六': 6,
    '七': 7, '八': 8, '九': 9, '十': 10
}
def extract_slots(text: str, threshold=80, tokenizer=None, is_tokenized=False) -> dict:
    """
    从文本中提取槽位信息

    Args:
        text: 输入文本
        threshold: 模糊匹配阈值
        tokenizer: 可选的外部分词器
        is_tokenized: 表示输入是否已分词

    Returns:
        dict: 提取到的槽位字典
    """
    slots = {}

    # 如果未分词且提供了分词器，则先进行分词
    if not is_tokenized and tokenizer:
        tokenized_text = tokenizer.tokenize(text)
    else:
        tokenized_text = text  # 使用原始文本或已分词文本

    # 预处理：插入空格，帮助 jieba 更好切分数字+量词+名词结构
    # tokenized_text = preprocess_text(tokenized_text)

    # 1. 数字型槽位提取
    slots.update(extract_numeric_slots(tokenized_text))

    # 2. 精确关键词匹配
    for slot_name, keywords in SLOT_DICT.items():
        matched = None

        # 精确匹配（基于分词后的结果）
        for keyword in keywords:
            if keyword in tokenized_text:
                matched = keyword
                break

        # 若未匹配，尝试模糊匹配
        if not matched:
            matched, score = process.extractOne(tokenized_text, keywords)
            if score < threshold:
                continue

        # 设置槽位值
        if slot_name in ["忌口", "过敏原"]:
            slots.setdefault(slot_name, []).append(matched)
        else:
            slots[slot_name] = matched

    return slots
def chinese_to_arabic(num_str):
    """将中文数字转换为阿拉伯数字"""
    result = 0
    tmp = 0
    for char in num_str:
        val = CHINESE_NUMBERS.get(char, 0)
        if val == 10:  # 处理带"十"的数字，如"十四"->14
            if tmp == 0:
                tmp = 1
            result += tmp * val
            tmp = 0
        else:
            tmp += val

    return result + tmp

def extract_numeric_slots(text):
    """统一提取数字型槽位"""
    numeric_slots = {}

        # 提取人数 - 扩展支持多种表达方式
    MIN_PERSONS = 1
    MAX_PERSONS = 20

    if m := re.search(r'(\d+)个?[人位份餐杯瓶盘碗]', text):
        count = int(m.group(1))
        if MIN_PERSONS <= count <= MAX_PERSONS:
            numeric_slots["人数"] = count
# 在 extract_numeric_slots 中使用
    if m := re.search(r'(一|二|两|三|四|五|六|七|八|九|十)[人杯位]', text):
        numeric_slots["人数"] = chinese_to_arabic(m.group(1))
    # 提取预算
    if m := re.search(r'(\d{2,4})元', text):
        numeric_slots["预算"] = int(m.group(1))

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
    text = "我想点两杯咖啡"
    # 提取槽位（自动调用 LTP 分词）
    slots = extract_slots(text, tokenizer=tokenizer)
    print(slots)


    test_cases = [
        "两杯咖啡",
        "三个人的套餐",
        "4位客人用餐",
        "五份披萨",
        "我要六瓶啤酒",
        "需要八盘凉菜",
        "九碗米饭"
    ]

    for text in test_cases:
        print(f"输入文本: {text}")
        print("提取结果:", extract_slots(text))
        print("-" * 30)

