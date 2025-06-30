# template_manager.py
import os
import time
import json
from pathlib import Path
import logging

class TemplateManager:
    def __init__(self, cache_dir="template_cache", refresh_interval=3600):
        """
        初始化模板管理器

        :param cache_dir: 本地缓存目录
        :param refresh_interval: 缓存刷新间隔（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.refresh_interval = refresh_interval
        self.local_cache = {}
        self.db_connection = None  # 数据库连接
        self.default_templates = {
            "basic": {
                "zh-CN": """你是一个智能服务员，请根据以下用户输入提供服务：
                
用户请求：{user_request}

请分析用户的请求并提供相应的服务。""",
                "en-US": """You are an intelligent waiter, please provide service based on the following user input:

User request: {user_request}

Please analyze the user's request and provide corresponding service."""
            },
            "role": {
                "zh-CN": """你是一个智能服务员，需要完成以下任务：
- 理解用户需求
- 提供餐厅服务
- 处理客户投诉
- 推荐特色菜品

当前用户请求：{user_request}

请根据上述要求处理用户请求。""",
                "en-US": """You are an intelligent waiter who needs to complete the following tasks:
- Understand user needs
- Provide restaurant services
- Handle customer complaints
- Recommend specialty dishes

Current user request: {user_request}

Please process the user request according to the above requirements."""
            },
            # ...其他默认模板...
        }
        self.context_templates = {
            "zh-CN": """你是一个智能服务员，正在与顾客进行对话。

对话历史：
{conversation_history}

最新请求：{user_request}

请基于对话历史处理最新请求。""",
            "en-US": """You are an intelligent waiter who is conversing with a customer.

Conversation history:
{conversation_history}

Latest request: {user_request}

Please process the latest request based on the conversation history."""
        }
        self.last_refresh_time = 0
        self.logger = logging.getLogger(__name__)

        # 创建缓存目录
        self.cache_dir.mkdir(exist_ok=True)

        # 加载本地缓存
        self._load_local_cache()

    def set_db_connection(self, db_connection):
        """设置数据库连接"""
        self.db_connection = db_connection

    def _load_local_cache(self):
        """从本地文件加载缓存"""
        try:
            for file_path in self.cache_dir.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    name = template_data["name"]
                    language = template_data["language"]
                    version = template_data["version"]

                    if name not in self.local_cache:
                        self.local_cache[name] = {}
                    if language not in self.local_cache[name]:
                        self.local_cache[name][language] = {}

                    self.local_cache[name][language][version] = template_data["content"]
        except Exception as e:
            self.logger.error(f"加载本地缓存失败: {str(e)}")

    def _save_to_local_cache(self, name, language, version, content):
        """将模板保存到本地缓存"""
        try:
            cache_file = self.cache_dir / f"{name}_{language}_{version}.json"
            template_data = {
                "name": name,
                "language": language,
                "version": version,
                "content": content
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)

            # 更新内存中的缓存
            if name not in self.local_cache:
                self.local_cache[name] = {}
            if language not in self.local_cache[name]:
                self.local_cache[name][language] = {}
            self.local_cache[name][language][version] = content

        except Exception as e:
            self.logger.error(f"保存到本地缓存失败: {str(e)}")

    def _check_cache_expired(self, name, language, version):
        """检查缓存是否过期"""
        cache_file = self.cache_dir / f"{name}_{language}_{version}.json"
        if not cache_file.exists():
            return True

        current_time = time.time()
        return current_time - cache_file.stat().st_mtime > self.refresh_interval

    def _get_from_local_cache(self, name, language, version):
        """从本地缓存获取模板"""
        if (self._check_cache_expired(name, language, version) or
                name not in self.local_cache or
                language not in self.local_cache[name] or
                version not in self.local_cache[name][language]):
            return None
        return self.local_cache[name][language][version]

    def _get_from_database(self, name, language, version=None):
        """从数据库获取模板"""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            if version:
                # 获取指定版本的模板
                query = """
                SELECT content FROM templates 
                WHERE name = %s AND language = %s AND version = %s AND is_active = TRUE
                """
                cursor.execute(query, (name, language, version))
            else:
                # 获取最新版本的模板
                query = """
                SELECT content, version FROM templates 
                WHERE name = %s AND language = %s AND is_active = TRUE
                ORDER BY updated_at DESC LIMIT 1
                """
                cursor.execute(query, (name, language))

            result = cursor.fetchone()

            if result:
                if version:
                    content = result[0]
                else:
                    content, version = result

                # 保存到本地缓存
                self._save_to_local_cache(name, language, version, content)
                return content

            return None

        except Exception as e:
            self.logger.error(f"从数据库获取模板失败: {str(e)}")
            return None
        finally:
            cursor.close()

    def _get_default_template(self, name, language):
        """获取默认模板"""
        if name in self.default_templates and language in self.default_templates[name]:
            return self.default_templates[name][language]
        # 返回基础模板作为最后备选
        return self.default_templates["basic"].get(language, self.default_templates["basic"]["en-US"])

    def get_template(self, name, language='zh-CN', version=None):
        """获取模板，支持热更新和版本控制"""
        # 1. 从本地缓存获取
        template = self._get_from_local_cache(name, language, version or "latest")

        if not template:
            # 2. 从数据库获取
            template = self._get_from_database(name, language, version)

        if not template:
            # 3. 使用默认模板
            template = self._get_default_template(name, language)

            # 如果请求了特定版本但未找到，则尝试获取最新版本
            if version and version != "latest":
                template = self.get_template(name, language)

        return template

    def update_template(self, name, language, version, content, activate=True):
        """更新模板（数据库和本地缓存）"""
        if not self.db_connection:
            raise Exception("数据库连接未设置")

        try:
            cursor = self.db_connection.cursor()

            # 插入新版本
            query = """
            INSERT INTO templates (name, language, version, content, is_active)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                content = VALUES(content),
                is_active = VALUES(is_active),
                updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (name, language, version, content, activate))

            # 提交事务
            self.db_connection.commit()

            # 更新本地缓存
            self._save_to_local_cache(name, language, version, content)

            # 如果激活，则更新最新版本标记
            if activate:
                latest_version_file = self.cache_dir / f"{name}_{language}_latest.json"
                with open(latest_version_file, "w", encoding="utf-8") as f:
                    json.dump({"latest_version": version}, f)

            return True

        except Exception as e:
            self.logger.error(f"更新模板失败: {str(e)}")
            self.db_connection.rollback()
            return False
        finally:
            cursor.close()

    def list_template_versions(self, name, language):
        """列出所有可用版本"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            query = """
            SELECT version, created_at FROM templates 
            WHERE name = %s AND language = %s
            ORDER BY created_at DESC
            """
            cursor.execute(query, (name, language))
            results = cursor.fetchall()

            return [{"version": row[0], "created_at": row[1]} for row in results]

        except Exception as e:
            self.logger.error(f"列出模板版本失败: {str(e)}")
            return []
        finally:
            cursor.close()

    def apply_template(self, text, language='zh-CN', template_name='basic', version=None):
        """应用指定模板"""
        template = self.get_template(template_name, language, version)
        try:
            return template.format(user_request=text)
        except KeyError as e:
            self.logger.error(f"模板格式错误，缺少必要参数: {str(e)}")
            return template  # 返回原始模板

    def get_context_template(self, language='zh-CN'):
        """获取上下文模板"""
        return self.context_templates.get(language, self.context_templates['en-US'])

    def apply_context_template(self, text, context, language='zh-CN', template_name='context'):
        """应用带上下文的模板"""
        template = self.get_context_template(language)
        return template.format(conversation_history=context, user_request=text)
