class NLUService:
    def parse(self, text: str) -> dict:
        # 可对接真实NLU模型，目前简化模拟逻辑
        result = {}
        if "天气" in text:
            result["天气状态"] = "寒冷" if "冷" in text else "炎热" if "热" in text else "晴朗"
        if "健身" in text or "健康" in text:
            result["健康偏好"] = "高蛋白"
        if any(word in text for word in ["情人节", "七夕", "圣诞"]):
            result["特殊节日"] = "情人节"
        if "不吃辣" in text:
            result["忌口"] = "不吃辣"
        if "对海鲜过敏" in text:
            result["过敏原"] = "海鲜"
        return result