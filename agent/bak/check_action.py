# agent/check_action.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from pathlib import Path
from logger import SignInLogger


STATE_FILE = Path("../assets/config/sign_state.json")
MAX_RETRY = 2

@AgentServer.custom_action("check_and_skip")
class CheckAndSkipAction(CustomAction):
    def run(self, context: Context, argv: dict) -> bool:
        # ✅ 从 custom_action_param 获取参数
        app_name = argv.get("app_name", "UnknownApp")
        
        logger = SignInLogger(STATE_FILE)
        status = logger.get_task_status(app_name)
        
        if status["success"]:
            print(f"[→] {app_name} 今日已成功签到，跳过")
            return False
        
        if status["attempts"] >= MAX_RETRY:
            print(f"[→] {app_name} 已达最大重试次数 ({MAX_RETRY})，跳过")
            return False
        
        print(f"[✓] {app_name} 开始签到 (第 {status['attempts']+1} 次尝试)")
        return True