"""
vector_db_initializer.py - 使用FAISS初始化向量数据库
"""

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 配置日志记录
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dish_data(file_name):
    try:
        file_path = os.path.join(os.getcwd(), file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print("文件前100字符内容:")
        print(content[:100])

        dishes = []
        current_cuisine = None
        dish_entries = {}

        lines = content.split('\n')

        for line in lines:
            line = line.strip()  # 去除前后空格
            if not line:
                continue

            # 匹配菜系标题（如 "### 鲁菜"）
            if line.startswith('### '):
                current_cuisine = line[4:].strip()
                logger.info(f"正在处理菜系：{current_cuisine}")
                dish_entries[current_cuisine] = {}
                continue

            # 匹配菜品名称（如 "**九转大肠**"）
            if line.startswith('**') and line.endswith('**'):
                dish_name = line[2:-2].strip()
                logger.debug(f"发现菜品：{dish_name}")
                dish_entries[current_cuisine][dish_name] = {
                    "features": {},
                    "description": ""
                }
                current_dish = dish_name
                continue

            # 匹配菜品属性（如 "- 口感：..."）
            if line.startswith('- '):
                feature_line = line[2:].strip()  # 去掉 "- " 前缀
                if ':' in feature_line:
                    key, value = feature_line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # 分类存储不同字段
                    if key in ['口感', '特点', '适合场景', '菜特点', '标签', '适合人群']:
                        if key == '特点':
                            dish_entries[current_cuisine][current_dish]["description"] = value
                        else:
                            dish_entries[current_cuisine][current_dish]["features"][key] = value

        # 转换为统一格式
        processed_dishes = []
        for cuisine, dishes in dish_entries.items():
            for dish_name, dish_info in dishes.items():
                combined_text = (
                    f"{dish_name} | "
                    f"菜系：{cuisine} | "
                    f"口感：{dish_info['features'].get('口感', '')} | "
                    f"特点：{dish_info['description']} | "
                    f"适合场景：{dish_info['features'].get('适合场景', '')} | "
                    f"菜特点：{dish_info['features'].get('菜特点', '')} | "
                    f"标签：{dish_info['features'].get('标签', '')} | "
                    f"适合人群：{dish_info['features'].get('适合人群', '')}"
                )

                processed_dishes.append({
                    "name": dish_name,
                    "cuisine": cuisine,
                    "text": combined_text
                })

        logger.info(f"成功解析 {len(processed_dishes)} 个菜品条目")
        return processed_dishes

    except Exception as e:
        logger.error(f"加载菜品数据失败：{e}")
        raise



def create_vector_database(dishes, model_name='all-MiniLM-L6-v2', output_dir='dish_vector_db'):
    """
    创建并保存FAISS向量数据库

    Args:
        dishes: 菜品数据列表
        model_name: 用于嵌入的模型名称
        output_dir: 输出目录

    Returns:
        tuple: (索引, 元数据)
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 加载预训练的句子嵌入模型
    logger.info(f"正在加载模型：{model_name}")
    model = SentenceTransformer(model_name)

    # 生成嵌入向量
    logger.info("正在生成嵌入向量...")
    sentences = [dish["text"] for dish in dishes]
    embeddings = model.encode(sentences, show_progress_bar=True)

    # 创建FAISS索引
    dimension = embeddings.shape[1]
    logger.info(f"创建维度为 {dimension} 的FAISS索引...")
    index = faiss.IndexFlatL2(dimension)

    # 添加向量到索引
    index.add(embeddings.astype(np.float32))

    # 保存索引和元数据
    logger.info(f"正在保存索引到 {output_dir} ...")
    faiss.write_index(index, os.path.join(output_dir, "dish_index.bin"))

    # 保存元数据
    metadata_file = os.path.join(output_dir, "metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(dishes, f, ensure_ascii=False, indent=2)

    logger.info(f"成功创建向量数据库！共包含 {len(dishes)} 个菜品")
    return index, dishes


def load_vector_database(db_dir='dish_vector_db'):
    """
    加载向量数据库

    Args:
        db_dir: 数据库目录

    Returns:
        tuple: (索引, 元数据)
    """
    logger.info(f"正在加载向量数据库 from {db_dir} ...")

    # 加载索引
    index = faiss.read_index(os.path.join(db_dir, "dish_index.bin"))

    # 加载元数据
    metadata_file = os.path.join(db_dir, "metadata.json")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    logger.info(f"成功加载包含 {index.ntotal} 条目的向量数据库")
    return index, metadata


def search_similar_dishes(index, metadata, query, top_k=5):
    """
    根据查询寻找最相似的菜品

    Args:
        index: FAISS索引
        metadata: 元数据
        query: 查询语句
        top_k: 返回结果数量

    Returns:
        list: 相似菜品列表
    """
    # 加载模型
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 对查询进行编码
    query_embedding = model.encode([query])

    # 执行搜索
    distances, indices = index.search(query_embedding.astype(np.float32), top_k)

    # 收集结果
    results = []
    for i in range(top_k):
        idx = indices[0][i]
        distance = distances[0][i]
        dish_info = metadata[idx]
        results.append({
            "score": float(1.0 / (1.0 + distance)),  # 将距离转换为分数
            **dish_info
        })

    return results


if __name__ == '__main__':
    # 文件路径
    file_path = 'dish'  # 包含您提供的完整菜品数据
    db_dir = 'dish_vector_db'

    # 步骤1：加载和处理数据
    dishes = load_dish_data(file_path)

    # 步骤2：创建向量数据库
    create_vector_database(dishes, output_dir=db_dir)

    # 步骤3：测试搜索功能
    index, metadata = load_vector_database(db_dir)

    test_queries = [
        "我想找一些辣的菜",
        "帮我推荐适合家庭聚餐的菜",
        "有什么适合宴请宾客的菜",
        "给我推荐几个经典的川菜",
        "我要找一些清淡养生的菜"
    ]

    for query in test_queries:
        print(f"\n{'='*50}\n查询：{query}")
        results = search_similar_dishes(index, metadata, query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} ({result['cuisine']})")
            print(f"   分数：{result['score']:.4f}")
            print(f"   描述：{result['text'][:200]}...")
