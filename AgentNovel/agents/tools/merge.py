from typing import Dict, List
from llm import get_response_from_llm


def merge_decisions(decisions: List[Dict[str, str]]) -> Dict[str, str]:
    input_text = (
        "以下是三条决策，请将它们合并为一条，并确保合并后的计划中包含明确的主语，并注意行为之间的逻辑性：\n"
    )
    for i, decision in enumerate(decisions, start=1):
        input_text += f"决策 {i}:\n"
        input_text += f"- 角色名: {decision['agent_name']}\n"
        input_text += f"- 目标: {decision['goal']}\n"
        input_text += f"- 计划: {decision['plan']}\n\n"

    input_text += (
        "请生成合并后的目标和计划，格式如下：\n"
        "目标: 合并后的目标内容\n"
        "计划: 合并后的计划内容（请确保计划中包含主语，且逻辑清晰），用一段话输出\n"        
    )

    # 调用大模型生成合并后的决策
    merged_response = get_response_from_llm(input_text)
    print(merged_response)  # 调试用，查看返回内容

    # 解析返回结果
    merged_goal = ""
    merged_plan = ""
    for line in merged_response.splitlines():
        if "目标:" in line:
            merged_goal = line.replace("目标:", "").strip()
        elif "计划:" in line:
            merged_plan = line.replace("计划:", "").strip()

    # 返回合并后的决策
    return {
        "agent_name": "合并",
        "goal": merged_goal,
        "plan": merged_plan,
    }