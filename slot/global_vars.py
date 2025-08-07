# E:\work\waiter\global_vars.py
"""
全局变量管理模块
用于在整个应用程序中共享配置和服务
"""

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局服务变量
GLOBAL_CONFIG = None
GLOBAL_TEMPLATE_MANAGER = None
GLOBAL_INTENT_CLASSIFIER = None
GLOBAL_TOKENIZER = None
_global_initialized = False

def initialize_global_services(config=None, intent_classifier=None, tokenizer=None):
    """
    初始化全局服务变量

    Args:
        config: 配置对象
        intent_classifier: 意图分类器实例
        tokenizer: 分词器实例
    """
    global GLOBAL_CONFIG, GLOBAL_TEMPLATE_MANAGER, GLOBAL_INTENT_CLASSIFIER, GLOBAL_TOKENIZER, _global_initialized

    if _global_initialized:
        return

    try:
        # 初始化配置
        from collector.templates.template import PromptTemplateLoader
        from intent.nlu_classifier import IntentClassifier
        from intent.classifier import IntentPredictor
        from dict.ltp_tokenizer import get_tokenizer

        GLOBAL_CONFIG = config

        # 加载模板管理器
        GLOBAL_TEMPLATE_MANAGER = PromptTemplateLoader()

        # 初始化意图分类器
        GLOBAL_INTENT_CLASSIFIER = _initialize_intent_classifier(intent_classifier, GLOBAL_CONFIG)

        # 初始化分词器
        GLOBAL_TOKENIZER = tokenizer or get_tokenizer()

        _global_initialized = True
        logger.info("全局服务初始化完成")

    except Exception as e:
        logger.error(f"初始化全局服务失败: {e}")
        raise

def _initialize_intent_classifier(intent_classifier, config):
    """
    初始化意图分类器

    Args:
        intent_classifier: 意图分类器实例
        config: 配置对象

    Returns:
        意图分类器实例
    """
    if intent_classifier:
        return intent_classifier

    use_ml_intent = getattr(config, "use_ml_intent", False)
    if use_ml_intent:
        try:
            from intent.classifier import IntentPredictor
            ml_classifier = IntentPredictor()
            if not getattr(ml_classifier, "is_trained", False):
                logger.info("开始训练意图分类模型")
                ml_classifier.train()
            return ml_classifier
        except Exception as e:
            logger.warning(f"加载机器学习意图分类器失败，回退到规则分类器: {e}")

    from intent.nlu_classifier import IntentClassifier
    return IntentClassifier()

def get_global_config():
    """获取全局配置"""
    if not _global_initialized:
        initialize_global_services()
    return GLOBAL_CONFIG

def get_global_template_manager():
    """获取全局模板管理器"""
    if not _global_initialized:
        initialize_global_services()
    return GLOBAL_TEMPLATE_MANAGER

def get_global_intent_classifier():
    """获取全局意图分类器"""
    if not _global_initialized:
        initialize_global_services()
    return GLOBAL_INTENT_CLASSIFIER

def get_global_tokenizer():
    """获取全局分词器"""
    if not _global_initialized:
        initialize_global_services()
    return GLOBAL_TOKENIZER

def is_global_initialized():
    """检查全局服务是否已初始化"""
    return _global_initialized
