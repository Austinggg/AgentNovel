import environment as env_module
scene_id = "scene_001"
environment = env_module.load_environment_by_scene_id(scene_id)

context = { 
                "environment": environment.__dict__,  # 包含环境信息
                "previous_decision": "123456789********" # 上一轮的合并决策
            }
print("Context for decision-making:", context)