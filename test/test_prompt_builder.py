import unittest
from unittest.mock import patch, MagicMock
from collector.prompt_builder.prompt import PromptBuilder
# 在文件开头添加 IntentClassifier 的导入语句（假设它定义在 collector.prompt 模块中）
from collector.prompt_builder.prompt import IntentClassifier


class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PromptBuilder(max_length=512)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='healthy_diet')
    def test_healthy_diet_intent(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        # 模拟输入与返回值
        input_text = "我想吃点清淡的，低脂一点，适合减脂"
        user_id = "U123456"
        location = "北京"

        mock_extract_slots.return_value = {
            "健康偏好": "低脂",
            "就餐形式": "桌餐"
        }
        mock_get_weather.return_value = {"weather": "晴朗", "temperature": 25}
        mock_get_order_history.return_value = ["水煮鱼", "麻婆豆腐"]
        mock_get_played_games.return_value = []

        # 调用 build_prompt
        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        # 断言模板是否正确
        self.assertIn("推荐菜品风格:", prompt)
        self.assertIn("少油少盐、清淡口味", prompt)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='game_recommendation')
    def test_game_recommendation_intent(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        input_text = "我们几个哥们想找个地方打麻将，最好能喝两瓶啤的"
        user_id = "U123456"
        location = "成都"

        mock_extract_slots.return_value = {
            "场景": "朋友聚会",
            "就餐环境": "有包间"
        }
        mock_get_weather.return_value = {"weather": "寒冷", "temperature": -5}
        mock_get_order_history.return_value = []
        mock_get_played_games.return_value = ["麻将", "斗地主"]

        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        self.assertIn("推荐玩法建议:", prompt)
        self.assertIn("麻将", prompt)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='festival')
    def test_festival_template(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        input_text = "我们想在圣诞节那天来一顿特别的晚餐，希望有点仪式感"
        user_id = "U123456"
        location = "上海"

        mock_extract_slots.return_value = {
            "特殊节日": "圣诞节",
            "就餐形式": "桌餐"
        }
        mock_get_weather.return_value = {"weather": "寒冷", "temperature": 0}
        mock_get_order_history.return_value = ["牛排", "红酒"]
        mock_get_played_games.return_value = []

        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        self.assertIn("节日限定套餐：", prompt)
        self.assertIn("烤火鸡、圣诞布丁、南瓜浓汤", prompt)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='order')
    def test_order_template(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        input_text = "我要点菜了，帮我推荐几道川菜"
        user_id = "U987654"
        location = "成都"

        mock_extract_slots.return_value = {
            "菜系": "川菜"
        }
        mock_get_weather.return_value = {"weather": "炎热", "temperature": 32}
        mock_get_order_history.return_value = ["回锅肉", "辣子鸡"]
        mock_get_played_games.return_value = []

        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        self.assertIn("推荐当地特色菜品如", prompt)
        self.assertIn("回锅肉\n辣子鸡", prompt)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='vegetarian')
    def test_vegetarian_template(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        input_text = "我是素食者，请给我推荐一些粤菜"
        user_id = "U789012"
        location = "广州"

        mock_extract_slots.return_value = {
            "忌口": "素食",
            "菜系": "粤菜"
        }
        mock_get_weather.return_value = {"weather": "多云", "temperature": 28}
        mock_get_order_history.return_value = ["白切鸡（素）", "蚝油生菜（素）"]
        mock_get_played_games.return_value = []

        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        self.assertIn("推荐素食菜品组合:", prompt)
        self.assertIn("蚝油生菜、香菇滑豆腐、素春卷", prompt)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='weather_based')
    def test_weather_based_cold(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        input_text = "外面太冷了，有什么热乎的可以吃？"
        user_id = None
        location = "哈尔滨"

        mock_extract_slots.return_value = {
            "天气状态": "寒冷"
        }
        mock_get_weather.return_value = {"weather": "寒冷", "temperature": -10}
        mock_get_order_history.return_value = []
        mock_get_played_games.return_value = []

        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        self.assertIn("推荐冬季暖身套餐:", prompt)
        self.assertIn("羊蝎子火锅、麻辣香锅、干锅牛肉", prompt)

    @patch('collector.prompt_builder.prompt.extract_slots')
    @patch('collector.prompt_builder.prompt.get_weather_by_location')
    @patch('collector.prompt_builder.prompt.get_user_order_history')
    @patch('collector.prompt_builder.prompt.get_user_played_games')
    @patch.object(IntentClassifier, 'classify', return_value='child_or_elderly')
    def test_child_or_elderly_template(
            self,
            mock_classify,
            mock_get_played_games,
            mock_get_order_history,
            mock_get_weather,
            mock_extract_slots
    ):
        input_text = "我带小孩来吃饭，有没有清淡点的菜？"
        user_id = "U123456"
        location = "深圳"

        mock_extract_slots.return_value = {
            "健康偏好": "清淡"
        }
        mock_get_weather.return_value = {"weather": "晴朗", "temperature": 30}
        mock_get_order_history.return_value = ["番茄炖豆腐", "鸡蛋羹"]
        mock_get_played_games.return_value = []

        prompt = self.builder.build_prompt(input_text, user_id=user_id, location=location)
        print(prompt)

        self.assertIn("推荐健康菜品:", prompt)
        self.assertIn("番茄炖豆腐、清炒时蔬、鸡蛋羹", prompt)


if __name__ == '__main__':
    unittest.main()
