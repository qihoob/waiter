import re
from collector.prompt_builder.config import SLOT_DICT, SLOT_ALIAS_MAP


def extract_slots(text: str) -> dict:
    """
    提取文本中的槽位信息，优先使用 SLOT_DICT 中的关键词，其次使用 SLOT_ALIAS_MAP 的别名
    """
    slots = {}

    # 提取数字型槽位
    if m := re.search(r'(\d+)人', text):
        slots["人数"] = int(m.group(1))
    if m := re.search(r'(\d{2,4})元', text):
        slots["预算"] = int(m.group(1))

    # 使用 SLOT_DICT 精确匹配
    for slot_name, keywords in SLOT_DICT.items():
        for keyword in keywords:
            if keyword in text:
                if slot_name in ["忌口", "过敏原"]:
                    # 支持多值字段
                    slots.setdefault(slot_name, []).append(keyword)
                else:
                    slots[slot_name] = keyword
                break

    # 使用 SLOT_ALIAS_MAP 进行模糊匹配
    for slot_name, aliases in SLOT_ALIAS_MAP.items():
        for alias in aliases:
            if alias in text:
                if slot_name in ["忌口", "过敏原"]:
                    slots.setdefault(slot_name, []).append(SLOT_DICT[slot_name][0])
                else:
                    slots[slot_name] = SLOT_DICT[slot_name][0]
                break

    return slots
