import yaml
from jinja2 import Environment, meta, Template, TemplateError
import os
import hashlib
import logging
from typing import Dict, Any, Set, List, Optional
from memory.local_cache import get_global_cache

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptTemplateLoader:
    """
    支持多目录、缓存和热更新的模板加载器

    特性：
    - 多个模板目录支持
    - 模板缓存提升性能
    - 热更新支持
    - 模板变量自动提取
    - 模板验证机制
    - ✅ 默认从当前目录加载模板
    """

    # 新增常量：默认模板文件名
    DEFAULT_TEMPLATE_FILE = "prompt_templates.yaml"
    
    def __init__(self, *template_file_paths):
        """
        初始化模板加载器

        Args:
            template_file_paths: 一个或多个YAML模板文件路径
        """
        self.templates = {}  # 存储所有模板
        self.template_hashes = {}  # 存储模板文件哈希值用于热更新
        self.template_cache = {}  # 缓存已编译的模板
        self.env = Environment()
        self.cache = get_global_cache()

        # 加载所有指定的模板文件
        for path in template_file_paths:
            self._load_template_file(path)

        logger.info(f"成功加载 {len(self.templates)} 个模板")

    def _load_template_file(self, file_path: str):
        """
        加载单个模板文件

        Args:
            file_path: YAML文件路径
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"模板文件不存在: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"模板文件格式错误: {file_path}, 错误: {e}")
        except Exception as e:
            raise Exception(f"读取模板文件失败: {file_path}, 错误: {e}")

        # 验证模板结构
        self._validate_template_structure(templates)

        # 存储模板
        for name, content in templates.items():
            self.templates[name] = content

        # 记录文件哈希值
        self.template_hashes[file_path] = self._get_file_hash(file_path)

    def _validate_template_structure(self, templates: Dict[str, Any]):
        """
        验证模板结构有效性

        Args:
            templates: 模板数据字典

        Raises:
            ValueError: 结构不合法时抛出异常
        """
        if not isinstance(templates, dict):
            raise ValueError("模板文件必须是字典格式")

        for name, content in templates.items():
            if not isinstance(content, dict):
                raise ValueError(f"模板 '{name}' 的内容必须是字典类型")

            for lang, template_str in content.items():
                if not isinstance(lang, str) or not isinstance(template_str, str):
                    raise ValueError(f"模板 '{name}' 的语言版本 '{lang}' 格式错误")

    def _get_file_hash(self, file_path: str) -> str:
        """
        获取文件哈希值

        Args:
            file_path: 文件路径

        Returns:
            str: SHA-1 哈希值
        """
        sha1_hash = hashlib.sha1()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha1_hash.update(chunk)
            return sha1_hash.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希值失败: {file_path}, 错误: {e}")
            raise

    def reload_templates(self):
        """重新加载所有模板（热更新）"""
        try:
            self.templates.clear()
            self.template_cache.clear()

            for file_path in self.template_hashes.keys():
                self._load_template_file(file_path)

            logger.info("模板已重新加载")
        except Exception as e:
            logger.error(f"重新加载模板失败: {e}")
            raise

    def get_template(self, template_name: str, lang: str = 'zh-CN', **kwargs) -> str:
        """
        获取并渲染模板

        Args:
            template_name: 模板名称
            lang: 语言版本
            kwargs: 上下文参数

        Returns:
            str: 渲染后的提示词
        """
        try:
            if template_name not in self.templates:
                raise ValueError(f"模板 {template_name} 不存在")

            if lang not in self.templates[template_name]:
                raise ValueError(f"模板 {template_name} 不支持语言 {lang}")

            raw_template = self.templates[template_name][lang]

            # 检查缓存
            cache_key = f"template:{template_name}:{lang}"
            cached_template = self.cache.get(cache_key)
            
            if cached_template and cached_template.get('content') == raw_template:
                template = cached_template.get('compiled')
            else:
                # 编译模板
                try:
                    template = self.env.from_string(raw_template)
                    # 缓存编译后的模板
                    self.cache.set(cache_key, {
                        'content': raw_template,
                        'compiled': template
                    }, expire_time=3600)  # 缓存1小时
                except TemplateError as e:
                    raise ValueError(f"模板语法错误: {e}")

            # 提取模板中使用的变量
            used_vars = self._extract_used_variables(raw_template)

            # 过滤掉模板中没有使用的变量
            filtered_context = {
                k: v for k, v in kwargs.items() if k in used_vars or k.startswith('_')
            }

            # 渲染模板
            return template.render(**filtered_context)
            
        except ValueError:
            # 重新抛出已知的值错误
            raise
        except Exception as e:
            logger.error(f"渲染模板失败: 模板={template_name}, 语言={lang}, 错误={e}")
            raise Exception(f"渲染模板失败: {e}")

    def _extract_used_variables(self, template_str: str) -> Set[str]:
        """
        提取模板中使用的变量名

        Args:
            template_str: 模板字符串

        Returns:
            set of variable names
        """
        try:
            ast = self.env.parse(template_str)
            return meta.find_undeclared_variables(ast)
        except Exception as e:
            logger.error(f"提取模板变量失败: {e}")
            return set()

    def list_templates(self) -> List[str]:
        """
        获取所有可用的模板名称

        Returns:
            list: 模板名称列表
        """
        return list(self.templates.keys())

    def get_template_languages(self, template_name: str) -> List[str]:
        """
        获取某个模板支持的语言版本

        Args:
            template_name: 模板名称

        Returns:
            list: 支持的语言列表
        """
        if template_name not in self.templates:
            raise ValueError(f"模板 {template_name} 不存在")

        return list(self.templates[template_name].keys())

    def get_template_info(self, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取模板信息

        Args:
            template_name: 可选，特定模板名称

        Returns:
            dict: 包含所有模板或特定模板的信息
        """
        if template_name:
            if template_name not in self.templates:
                raise ValueError(f"模板 {template_name} 不存在")

            return {
                "name": template_name,
                "versions": list(self.templates[template_name].keys()),
                "content": self.templates[template_name]
            }

        return {
            "total_templates": len(self.templates),
            "available_templates": list(self.templates.keys()),
            "languages": self._get_all_languages(),
            "file_paths": list(self.template_hashes.keys())
        }

    def _get_all_languages(self) -> List[str]:
        """
        获取所有支持的语言

        Returns:
            list: 所有语言版本列表
        """
        all_langs = set()
        for template in self.templates.values():
            all_langs.update(template.keys())
        return sorted(all_langs)

    def has_template(self, template_name: str) -> bool:
        """
        判断是否存在指定名称的模板

        Args:
            template_name: 模板名称

        Returns:
            bool: 是否存在该模板
        """
        return template_name in self.templates

    def has_language(self, template_name: str, lang: str) -> bool:
        """
        判断模板是否支持指定语言

        Args:
            template_name: 模板名称
            lang: 语言版本

        Returns:
            bool: 是否支持该语言
        """
        if template_name not in self.templates:
            return False

        return lang in self.templates[template_name]
