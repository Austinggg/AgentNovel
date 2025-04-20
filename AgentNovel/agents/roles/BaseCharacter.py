from llm import get_response_from_llm
import os
import json
class CharacterAgent:
    def __init__(self, name, personality, role, profession, health_status):
        self.name = name
        self.personality = personality
        self.role = role
        self.profession = profession
        self.health_status = health_status
        self.memory = []
        self.goal = []
        self.environment = None
        
    @staticmethod
    def generate_goal_with_cot(agent, context):
        """
        使用角色设定、环境信息和记忆，生成角色当前目标。
        """
        # 提取环境信息
        environment = context.get("environment", {})
        previous_decision = context.get("previous_decision", "无")

        # 构建 Prompt
        prompt = f"""
        你是小说中的角色「{agent.name}」，性格：{agent.personality}，职业：{agent.profession}，扮演的角色：{agent.role}，健康状态：{agent.health_status}。
        你记得：{''.join(agent.memory[-2:] if len(agent.memory) >= 2 else agent.memory)}。

        当前环境信息如下：
        - 场景编号：{environment.get('scene_id', '未知')}
        - 地点：{environment.get('location', '未知')}
        - 天气：{environment.get('weather', '未知')}
        - 氛围：{environment.get('atmosphere', '未知')}
        - 当前事件：{environment.get('event', '未知')}
        - 长期目标：{environment.get('long_term_goal', {}).get('description', '未知')}
        - 当前的环境目标：{environment.get('environment_goal', {}).get('description', '未知')}
        - 当前的环境目标状态：{environment.get('environment_goal', {}).get('status', '未知')}
        - 最近事件：{', '.join(environment.get('recent_events', []))}
        - 涉及的角色：{', '.join(environment.get('involved_characters', []))}

        上一轮的合并决策为：{previous_decision}

        请结合你的设定、记忆与当前环境，使用 Chain-of-Thought 的方式生成你**此刻最合理的目标**。
        目标应与当前环境目标和长期目标相关联，并推动情节发展。请仅返回最终目标句子。
        """
        # 调用 LLM 生成目标
        return get_response_from_llm(prompt)
    
    @staticmethod
    def plan_with_cot(agent, context):
        """
        使用角色背景与环境上下文，通过 CoT 推理生成下一步行动计划
        """
        prompt = f"""
        你是小说中的角色「{agent.name}」，性格：{agent.personality}，职业：{agent.profession}，扮演的角色：{agent.role}，当前健康状态：{agent.health_status},你的当前目标：{agent.goal},你记得：{agent.memory}。
        你目前处于一个特定环境中，环境信息如下：

        - 场景编号：{context['scene_id']}
        - 地点：{context['location']}
        - 天气：{context['weather']}
        - 氛围：{context['atmosphere']}
        - 当前事件：{context['event']}
        - 长期目标：{context['long_term_goal']}
        - 当前的环境目标：{context['environment_goal']}
        你拥有的记忆片段如下：{''.join(agent.memory)}

        请你使用「逐步思考（Chain-of-Thought）」的方式，详细描述你将如何达成当前目标。你应该分析环境、考虑自身状态与过往经验，并考虑当前完成环境目标是否有利于情节发展和提高情节张力。规划出你的行动计划。请使用清晰的推理过程+最终计划。

        输出格式：
        思考：
        - xxx
        - xxx
        计划：
        - 第一步：...
        - 第二步：...
        - 第三步：...
        """
        return get_response_from_llm(prompt)
    @staticmethod
    def plan_with_cot_next(agent, context, previous_decision):
        """
        使用角色背景、环境上下文和上一轮的合并决策，通过 CoT 推理生成下一步行动计划。
        """
        prompt = f"""
        你是小说中的角色「{agent.name}」，性格：{agent.personality}，职业：{agent.profession}，扮演的角色：{agent.role}，当前健康状态：{agent.health_status}。
        你的当前目标：{agent.goal}。
        你记得：{''.join(agent.memory)}。

        当前环境信息如下：
        - 场景编号：{context['scene_id']}
        - 地点：{context['location']}
        - 天气：{context['weather']}
        - 氛围：{context['atmosphere']}
        - 当前事件：{context['event']}
        - 长期目标：{context['long_term_goal']}
        - 当前的环境目标：{context['environment_goal']}
        你拥有的记忆片段如下：{''.join(agent.memory)}

        上一轮的合并决策如下：
        - 合并目标：{previous_decision['goal']}
        - 合并计划：{previous_decision['plan']}

        请你使用「逐步思考（Chain-of-Thought）」的方式，详细描述你将如何结合当前目标、环境信息和上一轮的合并决策，规划出你的下一步行动计划。
        你需要分析环境、考虑自身状态与过往经验，并判断如何在当前情境下推进情节发展和提高情节张力,尽可能和前面的决策产生区别。

        输出格式：
        思考：
        - xxx
        - xxx
        计划：
        - 第一步：...
        - 第二步：...
        - 第三步：...
        """
        return get_response_from_llm(prompt)

    def receive_environment(self, env):
        self.environment = env

        # 构建上下文信息
        context = {
            "scene_id": env.scene_id,
            "location": env.location,
            "weather": env.weather,
            "atmosphere": env.atmosphere,
            "event": env.event,
            "long_term_goal": env.long_term_goal
        }
        memory_file_path = os.path.join("resources", "character", f"{self.name}.json")
        if os.path.exists(memory_file_path):
            try:
                with open(memory_file_path, "r", encoding="utf-8") as memory_file:
                    memory_data = json.load(memory_file)
                    if isinstance(memory_data, list):
                        self.memory.extend(memory_data)
                    else:
                        print(f"警告：文件 {memory_file_path} 的内容格式不正确，期望为列表。")
            except Exception as e:
                print(f"读取记忆文件 {memory_file_path} 时出错：{e}")
        else:
                print(f"警告：记忆文件 {memory_file_path} 不存在。")

        goal = self.generate_goal_with_cot(self, context)
        self.goals.append(goal)