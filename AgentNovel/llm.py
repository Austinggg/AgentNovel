from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(api_key="", base_url="https://api.deepseek.com")

def get_response_from_llm(prompt: str) -> str:
    """
    调用 LLM 接口，传入 prompt，返回模型的回答。

    :param prompt: 用户输入的提示文本
    :return: 模型生成的回答
    """
    try:
        # 调用 OpenAI 接口生成回答
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        # 检查返回结果是否有效
        if not response or not hasattr(response, "choices") or not response.choices:
            return "请求失败: 返回结果无效"

        # 返回模型的回答
        return response.choices[0].message.content

    except Exception as e:
        # 捕获异常并返回错误信息
        return f"请求失败: {e}"

