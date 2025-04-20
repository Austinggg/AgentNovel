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
from llm import get_response_from_llm
from agents.tools.merge import merge_decisions
from write import generate_novel_from_decision  #合并决策的工具函数

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


#创建环境
def run_simulation(environment_dir: str, character_dir: str, outline_path: str, num_rounds: int = 3):
    """
    运行模拟环境，进行多轮决策并生成小说内容。

    参数:
        environment_dir: str，环境文件存储路径。
        character_dir: str，角色文件存储路径。
        outline_path: str，大纲文件路径。
        num_rounds: int，决策轮数，默认为 3。
    """
    decisions = []
    tmp = []

    # 获取最新的环境文件
    latest_scene_file = get_latest_scene_file(environment_dir)
    scene_id = os.path.splitext(os.path.basename(latest_scene_file))[0]
    environment = env_module.load_environment_by_scene_id(scene_id)

    # 获取所有角色
    agents = character_registry.get_all_characters(character_registry.CHARACTER_DIR)
    env_module.broadcast_to_characters(environment, agents)

    # 初始决策
    for name, agent in agents.items():
        goal = agent.generate_goal_with_cot(agent, environment.__dict__)
        agent.goal.append(goal)  # 将生成的目标添加到 agent 的 goal 属性中

        plan = agent.plan_with_cot(agent, environment.__dict__)
        tmp.append({
            "agent_name": name,
            "goal": goal,
            "plan": plan
        })
    merged_decision = merge_decisions(tmp)
    decisions.append(merged_decision)

    # 后续多轮决策
    for round_num in range(2, num_rounds + 1):
        print(f"\n=== Round {round_num} ===")
        tmp_next_round = []
        for name, agent in agents.items():
            # 结合 agent 自身、environment 和上一轮的决策内容进行新一轮决策
            context = {
                "environment": environment.__dict__,  # 包含环境信息
                "previous_decision": merged_decision  # 上一轮的合并决策
            }
            new_goal = agent.generate_goal_with_cot(agent, context)
            agent.goal = [new_goal]  # 将新目标覆盖原来的 agent 的 goal 属性

            new_plan = agent.plan_with_cot_next(agent, environment.__dict__, merged_decision)
            tmp_next_round.append({
                "agent_name": name,
                "goal": new_goal,
                "plan": new_plan
            })

        merged_decision = merge_decisions(tmp_next_round)
        decisions.append(merged_decision)

    # 背景信息
    backgound = {
        "environment": environment.__dict__,
        "personal_info": {name: agent.__dict__ for name, agent in agents.items()}
    }

    # 提取最佳决策
    llm_extractor_instance = llm_extractor.LLMExtractor()
    best = evaluate_decisions(decisions, llm_extractor_instance, backgound)
    decision = best[1]

    # 返回结果
    return decision, environment, agents, backgound