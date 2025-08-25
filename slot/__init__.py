# E:\work\waiter\slot\__init__.py
"""
Slot模块初始化文件
"""

from .SlotHandler import SlotHandler, SlotHandlerInterrupt
from .BaseSlotExtractionHandler import BaseSlotExtractionHandler
from .ContextBuildingSlotHandler import ContextBuildingSlotHandler
from .CuisineFlavorHandler import CuisineFlavorHandler
from .GameSlotHandler import GameSlotHandler
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

# 新增的处理器
from .AllergenSlotHandler import AllergenSlotHandler
from .DietaryRestrictionSlotHandler import DietaryRestrictionSlotHandler
from .DrinkSlotHandler import DrinkSlotHandler
from .FestivalSlotHandler import FestivalSlotHandler
from .ContextHistoryRetrievalHandler import ContextHistoryRetrievalHandler
from .ContextHistorySaveHandler import ContextHistorySaveHandler
from .SinglePersonSceneHandler import SinglePersonSceneHandler  # 新增一个人用餐场景处理器

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
    'CuisineFlavorHandler',
    'GameSlotHandler',
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

    # 新增的处理器
    'AllergenSlotHandler',
    'DietaryRestrictionSlotHandler',
    'DrinkSlotHandler',
    'FestivalSlotHandler',
    'GameSceneSlotHandler',
    'ContextHistoryRetrievalHandler',
    'ContextHistorySaveHandler',
    'SinglePersonSceneHandler',  # 新增一个人用餐场景处理器

    'initialize_global_services',
    'is_global_initialized',
    'get_global_config',
    'get_global_template_manager',
    'get_global_intent_classifier',
    'get_global_tokenizer'
]
