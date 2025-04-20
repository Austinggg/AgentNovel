import re
from LLM_DNF_Novel.models import llm_extractor
from agents.tools.memory import update_character_info
from decision import evaluate_decisions
import environment as env_module
import agents.roles.character_registry as character_registry
import json
import os
from typing import Dict, List
from agents.roles.BaseCharacter import CharacterAgent
from interact import run_simulation
from llm import get_response_from_llm
from agents.tools.merge import merge_decisions
from write import generate_novel_from_decision  #合并决策的工具函数

def check_outline_completion(outline_path: str, environment: dict, decision: dict) -> str:
    """
    检查大纲中的结局是否完成。
    :param outline_path: 大纲文件路径
    :param environment: 当前环境信息
    :param decision: 当前决策信息
    :return: "已完成" 或 "未完成"
    """
    with open(outline_path, "r", encoding="utf-8") as f:
        outline_data = json.load(f)
    ending = outline_data["ending"]
    ending_description = ending["description"]
    
    # 传入大纲中的ending的description，environment和decision
    prompt = f"""
    你是一个小说大纲分析助手。以下是当前环境信息和决策信息，请根据这些信息判断大纲中的ending是否完成。
    需要你完成以下任务：
    1. 结合环境和当前决策判断大纲中的ending是否完成。
    2. 如果完成，返回“已完成”；如果未完成，返回“未完成”。
    3.environment_dir: {environment_dir}
    4.character_dir: {character_dir}
    5.outline_path: {outline_path}
    6.scene_id: {scene_id}
    7.decision: {decision}
    8.environment: {environment.__dict__}
    9.ending_description: {ending_description}
    如果你认为大纲中的ending已经完成，返回“已完成”；如果未完成，返回“未完成”。
    """
    
    llm_response = get_response_from_llm(prompt)
    
    result = llm_response.strip()  

    # 验证返回结果是否符合预期
    if result not in ["已完成", "未完成"]:
        raise ValueError(f"大模型返回了无效的结果: {result}")

    return result

def get_latest_scene_file(directory: str) -> str:
    """
    从指定目录中获取命名中数字最大的 JSON 文件。
    :param directory: 文件所在目录
    :return: 数字最大的 JSON 文件路径
    """
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    # 提取文件名中的数字并排序
    files_with_numbers = [(f, int(re.search(r'\d+', f).group())) for f in files if re.search(r'\d+', f)]
    latest_file = max(files_with_numbers, key=lambda x: x[1])[0]
    return os.path.join(directory, latest_file)

if __name__ == "__main__":
    # 设置文件路径
    environment_dir = "resources/environment"
    character_dir = "resources/character"
    outline_path = "resources/outline/outline.json"

    # 初始化变量
    is_ending_complete = False  # 用于判断大纲的 ending 是否完成
    first_round = True          # 标记是否是第一轮

    while not is_ending_complete:
        # 运行模拟环境
        result = run_simulation(environment_dir, character_dir, outline_path, num_rounds=3)

        # 获取最新的环境文件
        decision = result[0]
        environment = result[1]
        agents = result[2]
        backgound = result[3]
        scene_id = os.path.splitext(os.path.basename(get_latest_scene_file(environment_dir)))[0]
        latest_scene_file = get_latest_scene_file(environment_dir)

        # 生成小说并保存为文件
        generate_novel_from_decision(decision, backgound)

        # 更新角色信息并保存到文件中
        update_character_info(agents, decision, character_dir)

        # 判断环境目标是否完成
        result = env_module.check_environment_goal_completion(decision, environment.__dict__, outline_path)
        # if result == "已完成":
        #     environment.complete_environment_goal()
        # else:
        #     print("环境目标未完成。")

        if environment.is_environment_goal_complete():
            print("环境目标已完成！")
            environment.complete_environment_goal()
            env_module.update_environment_by_scene_id(scene_id, environment, environment_dir, outline_path)

        # 如果不是第一轮，检查大纲的 ending 是否完成
        if not first_round:
            is_ending_complete = check_outline_completion(outline_path, environment.__dict__, decision) == "已完成"
            if is_ending_complete:
                print("大纲的 ending 已完成，程序结束。")
                break
        else:
            first_round = False  # 第一轮结束后，将标记设为 False
    
