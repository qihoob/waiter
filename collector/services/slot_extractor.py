import re
from collector.services.nlu_service import NLUService
from collector.config import SLOT_DICT

nlu = NLUService()

def extract_slots(text: str) -> dict:
    slots = {}
    if m := re.search(r'(\d+)人', text):
        slots["人数"] = int(m.group(1))
    if m := re.search(r'(\d{2,4})元', text):
        slots["预算"] = int(m.group(1))
    for slot, kws in SLOT_DICT.items():
        for kw in kws:
            if kw in text:
                slots[slot] = kw
                break
    nlu_slots = nlu.parse(text)
    return {**nlu_slots, **slots}