# agent/extract_action.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from pathlib import Path
from logger import SignInLogger

@AgentServer.custom_action("extract_code")
class ExtractCodeAction(CustomAction):
    def run(self, context: Context, argv: dict) -> bool:
        # ✅ 从 custom_action_param 获取参数
        app_name = argv.get("app_name", "UnknownApp")
        content_type = argv.get("content_type", "内容")
        content = argv.get("content", "")  # 实际项目中这里会从context获取
        
        if not content:
            # 模拟从context获取OCR结果
            # 实际应用中应从context.run_recognition结果中提取
            content = "TEST-CODE-12345"
        
        logger = SignInLogger(Path("../assets/config/sign_state.json"))
        logger.add_task_content(app_name, content_type, content)
        
        print(f"[🎁] {app_name} 提取到{content_type}: {content}")
        return True