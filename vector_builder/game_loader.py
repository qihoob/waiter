import os
import re
import logging
from typing import List, Dict, Optional

from vector_builder.faiss_db import VectorDB
from vector_builder.loader import DataLoader


class GameDataLoader(DataLoader):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def load(self, file_name: str) -> List[Dict]:
        """
        解析 game 格式文件，返回结构化数据列表

        Args:
            file_name: 文件名

        Returns:
            list: 包含 name、text 和 metadata 的游戏条目列表
        """
        file_path = os.path.join(os.getcwd(), file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到指定的文件：{file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.logger.info(f"成功加载文件 {file_name}，共 {len(content)} 字符")

        lines = [line.strip() for line in content.split('\n')]

        games = []
        current_game = None

        for idx, line in enumerate(lines):
            if not line:
                continue

            # 检测是否为游戏标题行
            title_match = re.search(r'#{2,5}(.+?)#{2,5}', line)
            if title_match:
                if current_game:
                    self._finalize_game_entry(current_game)
                    games.append(current_game)

                game_name = title_match.group(1).strip()
                self.logger.debug(f"发现新游戏：{game_name}")
                current_game = {
                    "name": game_name,
                    "metadata": {},
                    "features": {}
                }
                continue

            # 检测是否为属性行（支持 **key**: value 或 key**：value）
            prop_match = re.match(r'(?:[-*]|\d+\.)?\s*(?:\*\*|__)?(.+?)(?:\*\*|__)?:\s*(.+)', line)
            if prop_match and current_game is not None:
                key = prop_match.group(1).strip()
                value = prop_match.group(2).strip().rstrip('。')

                # 修复格式问题
                if key == '适合人数':
                    value = self._fix_player_count(value)

                if key in ['适合人数', '适合年龄', '游戏链接']:
                    self.logger.debug(f"添加属性：{key} - {value}")
                    current_game["metadata"][key] = value

        # 添加最后一个游戏
        if current_game:
            self._finalize_game_entry(current_game)
            games.append(current_game)

        self.logger.info(f"成功解析 {len(games)} 个游戏条目")
        return games

    def _fix_player_count(self, raw_value: str) -> str:
        """修复人数字段格式"""
        # 示例："24人" → "2-4人"
        match = re.search(r'(\d+)(?:-(\d+))?([^\d]+)', raw_value)
        if match:
            num = match.group(1)
            suffix = match.group(3)
            return f"{num}-{suffix}"

        # 示例："612人" → "6-12人"
        if re.match(r'\d+人$', raw_value):
            return raw_value

        return raw_value

    def _finalize_game_entry(self, game: Dict) -> Dict:
        """
        将 metadata 转换为 text 字段
        """
        meta = game['metadata']
        combined_text = (
            f"{game['name']} | "
            f"适合人数：{meta.get('适合人数', '')} | "
            f"适合年龄：{meta.get('适合年龄', '')} | "
            f"游戏链接：{meta.get('游戏链接', '')}"
        )
        game['text'] = combined_text
        game['features'] = meta.copy()
        return game


if __name__ == "__main__":
    # 实例化游戏数据加载器
    loader = GameDataLoader()
    items = loader.load("game")

    # 打印第一个游戏用于调试
    from pprint import pprint
    pprint(items[0])

    # 构建向量数据库
    vdb = VectorDB()
    vdb.build(items, "game_db", index_name="game")

    # 加载并搜索
    vdb.load("game_db", index_name="game")
    results = vdb.search("推荐适合家庭聚会的小游戏")
    print("\n搜索结果：")
    for r in results:
        print(f"{r['name']} (分数：{r['score']:.4f})")
        print(f"   链接：{r.get('游戏链接', '')}\n")
        print(f"   适合人数：{r.get('适合人数', '')}\n")
