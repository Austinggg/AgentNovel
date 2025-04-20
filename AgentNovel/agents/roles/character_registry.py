import os
import json
from typing import Dict
from agents.roles.BaseCharacter import CharacterAgent

CHARACTER_DIR = "resources/character"

def get_all_characters(character_dir: str) -> Dict[str, 'CharacterAgent']:
    agents = {}

    for filename in os.listdir(character_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(character_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 创建角色实例
            agent = CharacterAgent(
                name=data.get("name", "未知角色"),
                personality=data.get("personality", ""),
                role=data.get("role", ""),
                profession=data.get("profession", ""),
                health_status=data.get("health_status", "")
            )

            for mem in data.get("memory", []):
                agent.memory.append(mem)
            agent.goals = data.get("goals", [])

            # 使用角色名作为键
            agents[agent.name] = agent

    return agents
