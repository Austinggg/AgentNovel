
import json
import os
import re
from typing import Dict, List
from agents.roles.BaseCharacter import CharacterAgent
from agents.roles.character_registry import get_all_characters
from llm import get_response_from_llm

class Environment:
    def __init__(
        self,
        scene_id: str,
        location: str,
        event: str,
        weather: str,
        atmosphere: str,
        writing_style: str,
        recent_events: List[str],
        involved_characters: List[str],
        long_term_goal: str,
        current_interaction_goal: Dict[str, str],
        environment_goal: Dict[str, str]
    ):
        self.scene_id = scene_id
        self.location = location
        self.event = event
        self.weather = weather
        self.atmosphere = atmosphere
        self.writing_style = writing_style
        self.recent_events = recent_events
        self.involved_characters = involved_characters
        self.long_term_goal = long_term_goal
        self.current_interaction_goal = current_interaction_goal
        self.environment_goal = environment_goal

    def is_environment_goal_complete(self) -> bool:
        return self.environment_goal.get("status", "") == "已完成"

    def complete_environment_goal(self):
        self.environment_goal["status"] = "已完成"

    @staticmethod
    def from_json_file(path: str) -> 'Environment':
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Environment(**data)


def load_environment_by_scene_id(scene_id: str, base_path: str = "resources/environment") -> Environment:
    filename = f"{scene_id}.json"
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"环境文件不存在: {filepath}")
    return Environment.from_json_file(filepath)

def update_environment_by_scene_id(scene_id: str, environment: Environment, base_path: str = "resources/environment", outline_path: str = "resources/outline/outline.json") -> None:
    """
    更新环境文件，并生成一个新的环境文件，ID 比当前最大的序号大 1。
    
    参数:
        scene_id: 当前场景 ID（如 "scene_003"）。
        environment: 当前环境对象。
        base_path: 环境文件存储路径。
        outline_path: 大纲文件路径。
    """
    filename = f"{scene_id}.json"
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"环境文件不存在: {filepath}")
    
    # 加载最新结束环境文件
    with open(filepath, "r", encoding="utf-8") as f:
        latest_environment_data = json.load(f)
    
    # 加载大纲文件
    if not os.path.exists(outline_path):
        raise FileNotFoundError(f"大纲文件不存在: {outline_path}")
    with open(outline_path, "r", encoding="utf-8") as f:
        outline_data = json.load(f)
    
    # 提取 scene_id 的数字部分并递增
    match = re.search(r'\d+', scene_id)
    if not match:
        raise ValueError(f"无法从 scene_id 中提取数字: {scene_id}")
    new_scene_number = int(match.group()) + 1
    new_scene_id = f"scene_{new_scene_number:03d}"

    # 构造 LLM 提示
    prompt = f"""
    你是一个小说环境生成助手。以下是当前最新结束的环境信息、大纲信息和最佳决策，请根据这些信息生成一个新的环境。
    新的环境要满足以下目标：
    1. 满足 小说的逻辑发展。
    2. 满足 小说的情节发展。
    3. 满足 小说的角色发展。    
    4. 满足 小说的环境发展。
    5. 新环境要向大纲中的ending的description靠近
    6. 新环境要满足文学传作需求，即要有一定的文学性和情感深度。
    7. 新环境要有一定的悬念和冲突，以吸引读者的注意力。
    需要你完成以下任务：
    1. 根据最新环境信息，生成一个新的场景，场景 ID 为 {new_scene_id}。
    2. 新的场景需要在逻辑上与最新环境和最佳决策对最新环境造成的影响保持一致。
    3. 请确保生成的 JSON 格式与以下环境格式一致。
    返回内容仅包含如下部分（json格式）：
    scene_id、location、event、weather、atmosphere、writing_style、recent_events、involved_characters、long_term_goal、current_interaction_goal、environment_goal 
    最新环境信息如下：
    {json.dumps(latest_environment_data, ensure_ascii=False, indent=2)}

    大纲信息如下：
    {json.dumps(outline_data, ensure_ascii=False, indent=2)}

    最佳决策如下：
    {json.dumps(environment.__dict__, ensure_ascii=False, indent=2)}
"""

    # 调用大模型生成新环境
    llm_response = get_response_from_llm(prompt)
    llm_response_clean = llm_response.strip()
    if llm_response_clean.startswith("```json"):
        llm_response_clean = llm_response_clean.strip("```json").strip("```").strip()

    try:
        new_environment_data = json.loads(llm_response_clean)
    except json.JSONDecodeError:
        raise ValueError("大模型返回的内容无法解析为 JSON 格式，请检查提示或返回内容。")
    
    # 保存新的环境文件
    new_filepath = os.path.join(base_path, f"{new_scene_id}.json")
    with open(new_filepath, "w", encoding="utf-8") as f:
        json.dump(new_environment_data, f, ensure_ascii=False, indent=4)
    
    print(f"新的环境文件已生成: {new_filepath}")

def broadcast_to_characters(self, agents: Dict[str, CharacterAgent]) -> None:
    """
    向所有参与角色广播环境信息。

    :param agents: 角色字典，键为角色名，值为 CharacterAgent 对象。
    """
    for name in self.involved_characters:
        agent = agents.get(name)
        if agent:
                # 将当前环境赋值给角色的 environment 属性
            agent.environment = self
            print(f"[环境广播] 已将环境信息广播给角色: {name}")
        else:
            print(f"[环境广播] 警告：角色 {name} 未找到，无法广播环境信息")
        
def check_environment_goal_completion(best: dict, environment: dict, outline_path: str = "resources/outline/outline.json") -> str:
    """
    根据 best 决策、当前环境和大纲调用大模型，判断环境目标是否完成。

    参数:
        best: dict，最佳决策，包含 "agent_name", "goal", "plan" 等信息。
        environment: dict，当前环境信息。
        outline: dict，大纲信息。

    返回:
        str: "已完成" 或 "未完成"。
    """
    if not os.path.exists(outline_path):
        raise FileNotFoundError(f"大纲文件不存在: {outline_path}")
    with open(outline_path, "r", encoding="utf-8") as f:
        outline_data = json.load(f)
    
    # 构造 LLM 提示
    prompt = f"""
    你是一个小说环境目标判断助手，负责基于小说当前进展判断环境目标是否已经完成。

    请你完成以下任务：
    1. 阅读当前环境的环境目标（environment_goal），结合角色的最佳决策（即他们对当前环境的行为计划）与整部小说的大纲（包含主线目标与发展逻辑），判断该环境目标是否已经实现。
    2. 若当前环境目标已实现（即角色的行为已促成环境目标达成），请返回字符串："已完成"。
    3. 若尚未实现，请返回字符串："未完成"。
    4. 请只返回判断结果，不要解释说明。

    请注意：
    - 环境目标是该场景存在的意义，例如“邮轮失事”是邮轮场景的目标。
    - 你需要结合角色行为和剧情节奏进行合理判断，不可仅凭表面文字。
    - 通过决策的计划和目标来判断角色的行为是否促成了环境目标的达成。
    - 你可以参考大纲中的主线目标和发展逻辑来辅助判断。  

    角色的最佳决策如下：
    {json.dumps(best, ensure_ascii=False, indent=2)}

    当前环境信息如下：
    {json.dumps(environment, ensure_ascii=False, indent=2)}

    小说大纲如下：
    {json.dumps(outline_data, ensure_ascii=False, indent=2)}
    """

    # 调用大模型
    llm_response = get_response_from_llm(prompt)
    result = llm_response.strip()  

    # 验证返回结果是否符合预期
    if result not in ["已完成", "未完成"]:
        raise ValueError(f"大模型返回了无效的结果: {result}")

    return result        