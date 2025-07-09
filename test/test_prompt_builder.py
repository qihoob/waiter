import unittest
from prompt_builder import PromptBuilder

class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PromptBuilder(use_ml_intent=False)

    def test_clean_input(self):
        text = "   我想吃点低卡又清淡的菜，不吃海鲜。   "
        cleaned = self.builder._clean_input(text)
        self.assertEqual(cleaned, "我想吃点低卡又清淡的菜，不吃海鲜。")

    def test_tokenize(self):
        text = "我想吃点低卡又清淡的菜"
        tokenized = self.builder._chinese_tokenize(text)
        self.assertIn("低卡", tokenized.split())
        self.assertIn("清淡", tokenized.split())

    def test_extract_slots(self):
        text = "我想吃点低卡又清淡的菜，不吃海鲜。"
        tokenized_text = self.builder._chinese_tokenize(text)
        slots = extract_slots(tokenized_text)
        self.assertIn("健康偏好", slots)
        self.assertEqual(slots["健康偏好"], "低卡")
        self.assertIn("忌口", slots)
        self.assertIn("海鲜", slots["忌口"])

    def test_build_prompt(self):
        input_text = "我想吃点低卡又清淡的菜，不吃海鲜。"
        prompt = self.builder.build_prompt(input_text, location="北京")
        print(prompt)  # 可选：打印输出查看结构
        self.assertIn("当前用户请求：", prompt)
        self.assertIn("健康偏好：低卡", prompt)
        self.assertIn("忌口要求：海鲜", prompt)
        self.assertIn("当前天气：", prompt)
        self.assertIn("请根据以上信息综合判断并提供服务。", prompt)

    def test_game_recommendation_when_order_placed(self):
        input_text = "我们四个人来吃饭了，帮我推荐点餐前娱乐活动吧。"
        prompt = self.builder.build_prompt(input_text, is_order_placed=True, location="北京")
        print(prompt)
        self.assertIn("推荐玩法建议：", prompt)
        self.assertIn("麻将（包间内）", prompt)

    def test_city_based_dishes(self):
        dishes = self.builder._get_local_dishes("成都")
        self.assertIn("火锅", dishes)
        dishes_with_cuisine = self.builder._get_local_dishes("广州", "粤菜")
        self.assertIn("烧味", dishes_with_cuisine)

if __name__ == '__main__':
    unittest.main()
