import json
import os
from agents.roles import character_registry
from llm import get_response_from_llm
from pypinyin import lazy_pinyin
def update_character_info(agents: dict, decision_text: str, character_dir: str):
    """
    根据 agents 中的角色信息和新的剧情决策，更新角色状态（health_status、role、memory、goals等），
    并保存到对应的角色 JSON 文件中。

    参数:
        agents: dict，包含所有角色的字典，键为角色名，值为角色对象。
        decision_text: str，新剧情决策文本。
        character_dir: str，存储角色 JSON 文件的目录。
    """
    for name, agent in agents.items():
        # 加载角色的当前信息
        pinyin_name = ''.join(lazy_pinyin(name))
        character_file = os.path.join(character_dir, f"{pinyin_name}.json")
        if not os.path.exists(character_file):
            print(f"警告：角色文件 {character_file} 不存在，跳过更新。")
            continue

        with open(character_file, "r", encoding="utf-8") as file:
            character_data = json.load(file)
        # 构造 LLM 提示
        prompt = f"""
        你是一个小说角色管理助手。以下是一个小说角色的原始信息和一段新的剧情发展，请你根据剧情内容，更新角色的状态和记忆。
        需要你完成以下任务：
        1. 更新 health_status（如果剧情中出现角色伤势变化或处理）；
        2. 更新 role（如果角色承担了新任务或职责）；
        3. 从剧情总结出具体的记忆片段，结合以前的memory后更新memory，角色之前的memory是：{character_data["memory"]}；
        4. 归并总结memoy，不要让角色的memory那么臃肿
        请返回完整的 JSON 字典，格式和原始信息一致。

        原始角色信息如下：
        {json.dumps(character_data, ensure_ascii=False, indent=2)}

        新的剧情内容如下：
        "{decision_text}"
        """

        try:
    # 清洗模型输出
            llm_response = get_response_from_llm(prompt)
            llm_response_clean = llm_response.strip()
            if llm_response_clean.startswith("```json"):
                llm_response_clean = llm_response_clean.strip("```json").strip("```").strip()

            updated_data = json.loads(llm_response_clean)

            # 合并原有数据
            if os.path.exists(character_file):
                with open(character_file, "r", encoding="utf-8") as file:
                    old_data = json.load(file)
            else:
                old_data = {}

            old_data.update(updated_data)

            # 保存更新后的角色信息
            with open(character_file, "w", encoding="utf-8") as file:
                json.dump(old_data, file, ensure_ascii=False, indent=4)

            print(f"角色文件 {character_file} 已成功更新。")

        except Exception as e:
            print(f"角色 {name} 的信息更新失败: {e}")
            print(f"原始模型输出为：{llm_response}")

