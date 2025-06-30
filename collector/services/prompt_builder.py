from collector.services.template_manager import PromptTemplateManager

tpl_manager = PromptTemplateManager()

def select_templates(slots: dict) -> list:
    result = []
    if slots.get("健康偏好"): result.append("健康健身搭配")
    if slots.get("特殊节日") and slots.get("场景") == "情侣约会":
        result.append("情侣约会节日")
    if slots.get("场景") == "朋友聚会":
        result.append("朋友聚会娱乐")
    if slots.get("就餐环境") in ["正式", "安静"]:
        result.append("商务正式宴请")
    if slots.get("天气状态"):
        result.append("天气推荐")
    if slots.get("就餐形式"):
        result.append("快速简餐")
    if slots.get("忌口") or slots.get("过敏原"):
        result.append("带娃家庭聚餐")
    if not result:
        result.append("default")
    return result

def build_prompt(slots: dict) -> str:
    templates = select_templates(slots)
    return tpl_manager.render(templates, slots)