# agent/check_action.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from .logger import SignInLogger
from pathlib import Path

STATE_FILE = Path("../assets/config/sign_state.json")
MAX_RETRY = 2

@AgentServer.custom_action("check_and_skip")
class CheckAndSkipAction(CustomAction):
    def run(self, context: Context, argv) -> bool:
        # 1. 获取当前任务名（即 entry）
        task_id = context.get_task_id()
        if task_id == 0:
            print("[!] 无法获取任务ID")
            return False
        
        # 注意：context.get_task_id() 返回的是整数 ID，不是字符串 entry
        # 所以我们需要换一种方式获取 entry 名称
        
        # ✅ 更可靠的方式：约定 Pipeline 的第一个节点名为 "Init"
        # 并在 interface.json 的 task 定义中使用有意义的 entry 名
        # 然后通过日志文件中的记录来匹配
        
        # 2. 从上下文推断 App 名称（需约定）
        # 方案 A：要求每个 Pipeline 的 entry 名 = App 名（如 "Skland"）
        # 方案 B：在 CustomAction 参数中传入 app_name（推荐）
        
        # 📌 推荐：在 Pipeline 中显式传参
        app_name = argv.get("app_name", "UnknownApp")
        
        logger = SignInLogger(STATE_FILE)
        status = logger.get_task_status(app_name)
        
        if status["success"]:
            print(f"[→] {app_name} 今日已成功签到，跳过")
            return False  # 终止任务
        
        if status["attempts"] >= MAX_RETRY:
            print(f"[→] {app_name} 已达最大重试次数 ({MAX_RETRY})，跳过")
            return False  # 终止任务
        
        # 否则继续执行
        print(f"[✓] {app_name} 开始签到 (第 {status['attempts']+1} 次尝试)")
        return True