import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import threading

class VectorDB:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(VectorDB, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        if not hasattr(self, '_initialized'):
            self.model = SentenceTransformer(model_name)
            self.index = None
            self.metadata = None
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    def build(self, items, output_dir, index_name="default", batch_size=512):
        os.makedirs(output_dir, exist_ok=True)
        self.index = None
        total = len(items)
        for i in range(0, total, batch_size):
            batch = items[i:i+batch_size]
            sentences = [item["text"] for item in batch]
            embeddings = self.model.encode(sentences, show_progress_bar=False)
            if self.index is None:
                dim = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dim)
            self.index.add(embeddings.astype(np.float32))
        index_path = os.path.join(output_dir, f"{index_name}.bin")
        meta_path = os.path.join(output_dir, f"{index_name}_metadata.json")
        faiss.write_index(self.index, index_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        self.metadata = items
        self.logger.info(f"分批构建索引 {index_name} 完成，条目数：{total}")

    def load(self, db_dir, index_name="default"):
        index_path = os.path.join(db_dir, f"{index_name}.bin")
        meta_path = os.path.join(db_dir, f"{index_name}_metadata.json")
        self.index = faiss.read_index(index_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        self.logger.info(f"已加载索引 {index_name}，条目数：{self.index.ntotal}")

    def search(self, query, top_k=5):
        if self.index is None or self.metadata is None:
            raise RuntimeError("请先加载索引")
        query_emb = self.model.encode([query])
        distances, indices = self.index.search(query_emb.astype(np.float32), top_k)
        results = []
        for i in range(top_k):
            idx = indices[0][i]
            distance = distances[0][i]
            item = self.metadata[idx]
            results.append({
                "score": float(1.0 / (1.0 + distance)),
                **item
            })
        return results


    def add_to_index(self, new_items, db_dir, index_name="default"):
        # 加载现有索引
        index_path = os.path.join(db_dir, f"{index_name}.bin")
        meta_path = os.path.join(db_dir, f"{index_name}_metadata.json")
        self.index = faiss.read_index(index_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        # 向量化新数据
        new_sentences = [item["text"] for item in new_items]
        new_embeddings = self.model.encode(new_sentences, show_progress_bar=True)
        self.index.add(new_embeddings.astype(np.float32))

        # 更新元数据
        self.metadata.extend(new_items)

        # 保存更新后的索引和元数据
        faiss.write_index(self.index, index_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        self.logger.info(f"已向索引 {index_name} 添加新数据并保存")