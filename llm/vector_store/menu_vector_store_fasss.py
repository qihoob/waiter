from typing import List

import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from model.menu import MenuItem

class MenuVectorStore:
    def __init__(self, index_path: str = "menu_index.faiss"):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.index_path = index_path

        # 如果索引文件已存在，则加载索引
        try:
            self.index = faiss.read_index(self.index_path)
            print("FAISS index loaded from disk.")
        except:
            self.index = faiss.IndexFlatL2(300)  # 使用300维的向量空间
            print("FAISS index initialized.")

        self.menu_items = []
        self.menu_vectors = []

    def add_menu(self, menu: List[MenuItem]):
        descriptions = [item.description for item in menu]
        vectors = self.vectorizer.fit_transform(descriptions).toarray()  # 转化为向量
        self.menu_vectors.extend(vectors)
        self.menu_items.extend(menu)

        # FAISS 添加向量
        self.index.add(np.array(vectors, dtype=np.float32))

    def save_index(self):
        faiss.write_index(self.index, self.index_path)  # 保存 FAISS 索引到磁盘
        print("FAISS index saved to disk.")

    def search(self, query: str, k: int = 5) -> List[MenuItem]:
        query_vector = self.vectorizer.transform([query]).toarray().astype(np.float32)
        _, indices = self.index.search(query_vector, k)  # 获取最相似的 k 个菜单项

        return [self.menu_items[i] for i in indices[0]]

