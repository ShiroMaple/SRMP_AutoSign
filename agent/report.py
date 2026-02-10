# agent/report_action.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from pathlib import Path
from .logger import SignInLogger
from .notifier import send_to_serverchan

@AgentServer.custom_action("send_report")
class SendReportAction(CustomAction):
    def run(self, context: Context, argv) -> bool:
        logger = SignInLogger(Path("../assets/config/sign_state.json"))
        summary = logger.get_summary()
        send_to_serverchan("📱 每日签到完成", summary)
        return True
    
logger = SignInLogger()
summary = logger.get_summary()
send_to_serverchan("📱 签到完成", summary)