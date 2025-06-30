
from template.templates import TemplateManager

# 初始化模板管理器
template_manager = TemplateManager()

# 设置数据库连接（假设使用MySQL）
import mysql.connector
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "waiter_db"
}
db_connection = mysql.connector.connect(**db_config)
template_manager.set_db_connection(db_connection)