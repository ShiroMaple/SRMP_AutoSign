# agent/task_manager.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from pathlib import Path
from logger import SignInLogger

STATE_FILE = Path("../assets/config/sign_state.json")
MAX_RETRY = 2

# ==================== 流程控制：检查并跳过 ====================
@AgentServer.custom_action("check_and_skip")
class CheckAndSkipAction(CustomAction):
    """流程控制Action：检查状态决定是否跳过当前任务"""
    def run(self, context: Context, argv: dict) -> bool:
        app_name = argv.get("app_name", "UnknownApp")
        logger = SignInLogger(STATE_FILE)
        status = logger.get_task_status(app_name)
        
        if status["success"]:
            print(f"[→] {app_name} 今日已成功签到，跳过")
            return False  # 框架会跳过此节点后续操作
        
        if status["attempts"] >= MAX_RETRY:
            print(f"[→] {app_name} 已达最大重试次数 ({MAX_RETRY})，跳过")
            return False
        
        print(f"[✓] {app_name} 开始签到 (第 {status['attempts']+1} 次尝试)")
        return True  # 继续执行后续节点

# ==================== 状态记录：统一处理所有状态操作 ====================
@AgentServer.custom_action("update_task_status")
class UpdateTaskStatusAction(CustomAction):
    """
    统一状态管理器：通过 operation 参数控制行为
    支持操作: mark_success | mark_failed | log_error | reset
    """
    def run(self, context: Context, argv: dict) -> bool:
        operation = argv.get("operation", "mark_success")
        app_name = argv.get("app_name", "UnknownApp")
        error_type = argv.get("error_type", "")
        logger = SignInLogger(STATE_FILE)
        
        # 未来扩展：可从 context 获取识别结果自动判断状态
        # if operation == "auto_detect":
        #     reco_result = context.get_last_recognition_result()
        #     operation = "mark_success" if reco_result.hit else "mark_failed"
        
        if operation == "mark_success":
            logger.mark_success(app_name)
            print(f"[✓] {app_name} 签到成功！")
        
        elif operation == "mark_failed":
            logger.mark_failed(app_name)
            print(f"[✗] {app_name} 签到失败！")
        
        elif operation == "log_error":
            print(f"[!] {app_name} 错误: {error_type or '未知错误'}")
            # 可扩展：记录到详细日志文件
        
        elif operation == "reset":
            logger.reset_task(app_name)
            print(f"[↺] {app_name} 状态已重置")
        
        else:
            print(f"[?] 未知操作 '{operation}'，忽略")
        
        return True  # 始终返回True，不影响流程继续