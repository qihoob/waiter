import os
import mysql.connector
from mysql.connector import pooling
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接池配置
_db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "waiter_db"),
    "charset": "utf8mb4",
    "autocommit": True,
    "pool_name": "waiter_pool",
    "pool_size": 5,
    "pool_reset_session": True
}

# 创建连接池
try:
    _connection_pool = pooling.MySQLConnectionPool(**_db_config)
    logger.info("数据库连接池创建成功")
except Exception as e:
    logger.error(f"数据库连接池创建失败: {e}")
    _connection_pool = None

def get_db_connection():
    """
    获取数据库连接
    
    Returns:
        MySQLConnection: 数据库连接对象
    """
    if not _connection_pool:
        raise Exception("数据库连接池未初始化")
    
    try:
        connection = _connection_pool.get_connection()
        return connection
    except Exception as e:
        logger.error(f"获取数据库连接失败: {e}")
        raise

def get_user_order_history(user_id, limit=10):
    """
    获取用户历史订单
    
    Args:
        user_id (str): 用户ID
        limit (int): 返回记录数限制
        
    Returns:
        list: 历史订单列表
    """
    if not user_id:
        return []
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, user_id, order_content, created_at 
        FROM user_orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return results
    except Exception as e:
        logger.error(f"获取用户订单历史失败: {e}")
        return []

def get_user_played_games(user_id, limit=10):
    """
    获取用户历史游戏记录
    
    Args:
        user_id (str): 用户ID
        limit (int): 返回记录数限制
        
    Returns:
        list: 历史游戏记录列表
    """
    if not user_id:
        return []
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, user_id, game_name, played_at 
        FROM user_games 
        WHERE user_id = %s 
        ORDER BY played_at DESC 
        LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return results
    except Exception as e:
        logger.error(f"获取用户游戏历史失败: {e}")
        return []
