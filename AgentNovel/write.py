import os
from llm import get_response_from_llm

def generate_novel_from_decision(decision: dict, background: dict):
    """
    根据决策和背景调用大模型生成文学创作，并以递增数字命名存储为txt文件。
    
    :param decision: 包含 "agent_name", "goal", "plan" 的决策字典。
    :param background: 包含环境和个人信息的背景字典。
    """
    # 提取环境和个人信息
    environment = background.get("environment", {})
    personal_info = background.get("personal_info", {})

    # 提取创作风格和文风
    atmosphere = environment.get("atmosphere", "未知氛围")
    writing_style = environment.get("writing_style", "未知文风")

    # 生成输入文本
    input_text = (
        f"你是一个小说创作大师，以下是你需要创作的背景和决策信息：\n\n"
        f"请对于当前环境进行完整详实且富有文学性的描述，不要随意跳出环境的限制，如果角色的决策需要去环境之外完成，那么就稍微描写即可.只生成一章的内容（大概3200字）\n"
        f"请注意，注意你创作的情节的完整性。\n\n"
        f"以下是当前环境和背景信息：\n"
        f"环境：{environment}\n"
        f"个人信息：{personal_info}\n\n"
        f"以下是决策信息：\n"
        f"角色名: {decision['agent_name']}\n"
        f"目标: {decision['goal']}\n"
        f"计划: {decision['plan']}\n\n"
        f"请根据以上信息创作一段文学作品，要求：\n"
        f"1. 文风：{writing_style}。\n"
        f"2. 氛围：{atmosphere}。\n"
        f"3. 以第三人称视角叙述。\n"
        f"4. 语言生动，情节紧凑，符合背景和环境。\n"
        f"5. 体现角色的目标和计划。\n"
        f"6. 输出格式为一章完整的小说（至少3000字）。\n"
    )

    # 调用大模型生成文本
    generated_text = get_response_from_llm(input_text)

    # 确定存储路径
    output_dir = "resources/novel"
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在

    # 获取当前目录下的所有以数字命名的txt文件
    existing_files = [f for f in os.listdir(output_dir) if f.endswith(".txt") and f[:-4].isdigit()]
    existing_numbers = sorted(int(f[:-4]) for f in existing_files)
    next_number = existing_numbers[-1] + 1 if existing_numbers else 1  # 计算下一个文件编号

    # 保存生成的文本
    output_path = os.path.join(output_dir, f"{next_number}.txt")
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(generated_text)

    print(f"文学作品已生成并保存至 {output_path}")