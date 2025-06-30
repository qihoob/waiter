from schema import PromptInput
from slot_extractor import extract_slots
from context_loader import get_user_context
from template_engine import render_prompt

def build_prompt(user_input: str, user_id: str) -> str:
    intent = extract_slots(user_input)
    context = get_user_context(user_id)
    prompt_input = PromptInput(intent=intent, context=context)
    return render_prompt(prompt_input.dict())
