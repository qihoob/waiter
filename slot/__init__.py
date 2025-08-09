# E:\work\waiter\slot\__init__.py
"""
Slot模块初始化文件
"""

from .SlotHandler import SlotHandler, SlotHandlerInterrupt
from .BaseSlotExtractionHandler import BaseSlotExtractionHandler
from .ContextBuildingSlotHandler import ContextBuildingSlotHandler
from .CuisineSlotHandler import CuisineSlotHandler
from .GameRecommendationSlotHandler import GameRecommendationSlotHandler
from .HealthPreferenceSlotHandler import HealthPreferenceSlotHandler
from .LocationSlotHandler import LocationSlotHandler
from .MissingSlotCompletionHandler import MissingSlotCompletionHandler
from .OrderDetectionSlotHandler import OrderDetectionSlotHandler
from .PeopleCountSlotHandler import PeopleCountSlotHandler
from .SceneSlotHandler import SceneSlotHandler
from .TasteSlotHandler import TasteSlotHandler
from .TemplateRenderingSlotHandler import TemplateRenderingSlotHandler
from .TemplateSelectionSlotHandler import TemplateSelectionSlotHandler
from .TextCleaningSlotHandler import TextCleaningSlotHandler
from .TokenizationSlotHandler import TokenizationSlotHandler
from .UserDataSlotHandler import UserDataSlotHandler
from .WeatherSlotHandler import WeatherSlotHandler

# 移除旧的处理器导入
# from .SlotValidationHandler import SlotValidationHandler  # 移除这一行

# 添加新的处理器导入
from .ContextHistoryRetrievalHandler import ContextHistoryRetrievalHandler
from .ContextHistorySaveHandler import ContextHistorySaveHandler

from .global_vars import (
    initialize_global_services,
    is_global_initialized,
    get_global_config,
    get_global_template_manager,
    get_global_intent_classifier,
    get_global_tokenizer
)

__all__ = [
    'SlotHandler',
    'SlotHandlerInterrupt',
    'BaseSlotExtractionHandler',
    'ContextBuildingSlotHandler',
    'CuisineSlotHandler',
    'GameRecommendationSlotHandler',
    'HealthPreferenceSlotHandler',
    'LocationSlotHandler',
    'MissingSlotCompletionHandler',
    'OrderDetectionSlotHandler',
    'PeopleCountSlotHandler',
    'SceneSlotHandler',
    'TasteSlotHandler',
    'TemplateRenderingSlotHandler',
    'TemplateSelectionSlotHandler',
    'TextCleaningSlotHandler',
    'TokenizationSlotHandler',
    'UserDataSlotHandler',
    'WeatherSlotHandler',
    'initialize_global_services',
    'is_global_initialized',
    'get_global_config',
    'get_global_template_manager',
    'get_global_intent_classifier',
    'get_global_tokenizer',
    # 移除旧的处理器
    # 'SlotValidationHandler',  # 移除这一行
    # 添加新的处理器
    'ContextHistoryRetrievalHandler',
    'ContextHistorySaveHandler'
]
