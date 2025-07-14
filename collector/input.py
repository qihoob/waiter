# input_collector.py
from flask import jsonify, request,render_template
from constant.constant import MAX_INPUT_LENGTH
import os
import speech_recognition as sr

from intent.classifier import IntentPredictor
from prompt_builder.prompt import PromptBuilder
from vector_builder.dish_loader import DishDataLoader
from vector_builder.faiss_db import VectorDB
from vector_builder.game_loader import GameDataLoader


class InputCollector:
    def __init__(self, app):
        self.app = app
        self.LOGGER = app.logger
        self.recognizer = sr.Recognizer()
        self.MAX_INPUT_LENGTH = MAX_INPUT_LENGTH

        self.predictor = IntentPredictor()
        self.property = PromptBuilder()

        self.vdb = VectorDB()

    def register_routes(self):
        """注册路由"""
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/submit/text', methods=['POST'])
        def handle_text():
            """
            处理文本输入的路由
            支持JSON和表单格式的输入
            """
            content_type = request.headers.get('Content-Type')

            try:
                if content_type == 'application/json':
                    data = request.get_json()
                    user_text = data.get("text", "")
                elif content_type == 'application/x-www-form-urlencoded':
                    user_text = request.form.get("text", "")
                else:
                    self.LOGGER.error(f"不支持的Content-Type: {content_type}")
                    return jsonify({"error": "不支持的Content-Type"}), 415

                # 输入为空处理
                if not user_text:
                    self.LOGGER.warning("收到空文本输入")
                    return jsonify({"error": "文本不能为空"}), 400

                # 输入长度检查
                if len(user_text) > self.MAX_INPUT_LENGTH:
                    self.LOGGER.warning(f"输入文本过长: {len(user_text)} > {self.MAX_INPUT_LENGTH}")
                    return jsonify({"error": f"输入文本过长，超过{self.MAX_INPUT_LENGTH}字符"}), 413

                # 记录输入内容（只记录前50个字符以保护隐私）
                self.LOGGER.info(f"收到文本输入: {user_text[:50]}...")

                #处理用户输入，对输入进行意图判断
                intent  = self.predictor.classify(user_text)

                index_name = "dish"
                #根据意图选择索引库
                if intent in ["game_recommendation"]:
                    index_name = "game"
                    self.vdb.load("game_db", index_name="game")
                else:
                    self.vdb.load("dish_db", index_name="dish")
                #从向量数据库获取推荐数据
                recommendation = self.vdb.search(user_text, top_k=1)
                prompt = self.property.build_prompt(user_text, intent=intent, recommendation=recommendation)


                #查询大模型
                response = self.property.query_model(prompt)



                # 返回成功响应
                return jsonify({
                    "type": "text",
                    "content": user_text
                })

            except Exception as e:
                self.LOGGER.error(f"处理文本输入时出错: {str(e)}", exc_info=True)
                return jsonify({"error": "内部服务器错误"}), 500

        @self.app.route('/upload/audio', methods=['POST'])
        def handle_audio():
            if 'file' not in request.files:
                return jsonify({"error": "缺少音频文件"}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "未选择文件"}), 400

            try:
                # 创建存储目录（如果不存在）
                storage_dir = os.path.join(os.getcwd(), 'audio_uploads')
                os.makedirs(storage_dir, exist_ok=True)

                # 构建安全的文件路径
                filename = os.path.basename(file.filename)  # 防止路径遍历攻击
                file_path = os.path.join(storage_dir, filename)

                # 保存并处理文件
                file.save(file_path)
                text = self.recognize_audio(file_path)

                # 处理完成后清理
                os.remove(file_path)

                if not text:
                    return jsonify({"error": "无法识别音频内容"}), 500

                return jsonify({
                    "type": "audio",
                    "content": text
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500


    def recognize_audio(self, file_path):
        """执行实际的语音识别操作"""
        with sr.AudioFile(file_path) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio, language="zh-CN")
                self.LOGGER.info(f"成功识别音频内容为: {text}")
                return text
            except sr.UnknownValueError:
                self.LOGGER.warning("Google 无法理解音频内容")
                return None
            except sr.RequestError as e:
                error_msg = f"Google 语音识别服务错误: {e}"
                self.LOGGER.error(error_msg)
                raise Exception(error_msg)

