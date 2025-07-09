import os
import logging

from vector_builder.faiss_db import VectorDB
from vector_builder.loader import DataLoader


class DishDataLoader(DataLoader):
    def load(self, file_name):
        try:
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            dishes = []
            current_cuisine = None
            dish_entries = {}

            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('### '):
                    current_cuisine = line[4:].strip()
                    dish_entries[current_cuisine] = {}
                    continue
                if line.startswith('**') and line.endswith('**'):
                    dish_name = line[2:-2].strip()
                    dish_entries[current_cuisine][dish_name] = {
                        "features": {},
                        "description": ""
                    }
                    current_dish = dish_name
                    continue
                if line.startswith('- '):
                    feature_line = line[2:].strip()
                    if ':' in feature_line:
                        key, value = feature_line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in ['口感', '特点', '适合场景', '菜特点', '标签', '适合人群']:
                            if key == '特点':
                                dish_entries[current_cuisine][current_dish]["description"] = value
                            else:
                                dish_entries[current_cuisine][current_dish]["features"][key] = value

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
            logging.info(f"成功解析 {len(processed_dishes)} 个菜品条目")
            return processed_dishes
        except Exception as e:
            logging.error(f"加载菜品数据失败：{e}")
            raise

# 可扩展 MovieDataLoader, BookDataLoader 等
if __name__ == "__main__":
    # 实例化菜品数据加载器
    dish_loader = DishDataLoader()
    # 加载菜品数据，返回处理后的条目列表
    items = dish_loader.load("dish")

    # 假设有电影数据加载器和数据
    # from vector_builder.loader.movie_loader import MovieDataLoader
    # movie_loader = MovieDataLoader()
    # other_items = movie_loader.load("movie.txt")
    other_items = []  # 示例：实际应加载真实数据

    # 实例化向量数据库
    vdb = VectorDB()
    # 构建菜品索引
    vdb.build(items, "dish_db", index_name="dish")

    # 加载菜品索引并查询
    vdb.load("dish_db", index_name="dish")
    results = vdb.search("推荐川菜")
    print(results)