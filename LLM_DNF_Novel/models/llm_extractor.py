import openai
from utils.prompt_templates import PROMPT_TEMPLATES

class LLMExtractorAPI:
    def __init__(self, model="gpt-3.5-turbo", api_key_file="api_key.txt"):
        """
        初始化 LLM 提取器
        :param model: 使用的模型名称（如 gpt-3.5-turbo 或 gpt-4）
        :param api_key_file: 存储 API 密钥的文件路径
        """
        # 从文件中读取 API 密钥
        try:
            with open(api_key_file, "r") as f:
                self.api_key = f.read().strip()
        except FileNotFoundError:
            raise ValueError(f"API key file '{api_key_file}' not found. Please create it and add your OpenAI API key.")
        except Exception as e:
            raise ValueError(f"Error reading API key file: {e}")

        openai.api_key = self.api_key
        self.model = model

    def extract_logic_atoms(self, text, task="General"):
        """
        使用 OpenAI API 提取逻辑原子
        :param text: 输入的文本
        :param task: 使用的任务模板（General 或 TaskSpecific）
        :return: 提取的逻辑原子字典
        """
        # 获取任务模板
        prompts = PROMPT_TEMPLATES.get(task, {})
        if not prompts:
            raise ValueError(f"Task '{task}' not found in PROMPT_TEMPLATES.")

        logic_atoms = {}

        for key, prompt in prompts.items():
            full_prompt = f"{prompt}\nText: {text}\n"

            # 调用 OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for evaluating text quality."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=512,
                    temperature=0.7
                )
                logic_atoms[key] = response['choices'][0]['message']['content'].strip()
            except openai.error.OpenAIError as e:
                print(f"Error during API call for {key}: {e}")
                logic_atoms[key] = "Error"
        return logic_atoms