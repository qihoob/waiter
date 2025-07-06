from langchain.tools import Tool


def confirm_order(input: str):
    if "确认下单" in input or "下单" in input:
        return "确认下单"
    return "继续对话"


confirm_order_checker_tool = Tool.from_function(
    func=confirm_order,
    name="ConfirmOrderChecker",
    description="识别是否用户想确认下单，如果提示中包含确认下单的意图，则返回'确认下单'"
)
