from typing import List, Optional, Literal
from pydantic import BaseModel

class UserIntent(BaseModel):
    intent_type: Literal["点菜", "推荐游戏", "其他"]
    scene: Optional[str]
    party_size: Optional[int]
    preferences: List[str] = []
    modality: Optional[str] = "文本"

class PromptContext(BaseModel):
    time: Optional[str]
    weather: Optional[str]
    location: Optional[str]
    history: List[str] = []
    user_id: Optional[str]

class PromptInput(BaseModel):
    intent: UserIntent
    context: PromptContext
