# agent/my_action.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

# ==============================================================================
# 全局配置/常量定义
# ==============================================================================

# ==============================================================================
# 工具函数（通用辅助功能）
# ==============================================================================

# ==============================================================================
# custom_action（用户数据处理）
# ==============================================================================
@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        print("my_action_111 is running!")

        return True

# ==============================================================================
# 主程序入口
# ==============================================================================
def main():
    # 加载原始数据
    #raw_user_data = load_user_data()
    #print(f"原始用户数据：{raw_user_data}")
    
    # 格式化数据
    #formatted_data = format_user_data(raw_user_data)
    #print(f"格式化后数据：{formatted_data}")
    
    # 保存处理后的数据
    #with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
    #    json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print("Hello, World!")

if __name__ == "__main__":
    main()