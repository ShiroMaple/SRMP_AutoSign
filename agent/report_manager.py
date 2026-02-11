# agent/report_manager.py
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from pathlib import Path
from logger import SignInLogger
from notifier import send_to_serverchan
import json
import pprint

# ==================== 内容提取 ====================
@AgentServer.custom_action("extract_content")
class ExtractContentAction(CustomAction):
    """提取任务特定内容（如兑换码），支持模拟和真实模式"""
    def run(self, context: Context, argv: dict) -> bool:
        app_name = argv.get("app_name", "UnknownApp")
        content_type = argv.get("content_type", "内容")
        # 优先使用传入内容（测试用），未来可扩展从context获取
        content = argv.get("content") or f"模拟{content_type}"
        
        logger = SignInLogger(Path("../assets/config/sign_state.json"))
        logger.add_task_content(app_name, content_type, content)
        print(f"[🎁] {app_name} 提取到{content_type}: {content}")
        return True

# ==================== 报告发送 ====================
@AgentServer.custom_action("send_report")
class SendReportAction(CustomAction):
    
    """发送汇总报告，自动包含所有任务状态和提取内容
    def run(self, context: Context, argv: dict) -> bool:
        extra_content = argv.get("extra_content", "")
        logger = SignInLogger(Path("../assets/config/sign_state.json"))
        summary = logger.get_summary()
        
        if extra_content:
            summary += f"\n\n📢 附加提示:\n{extra_content}"
        
        # 自动添加执行统计
        tasks = logger._cache.get("tasks", {})
        total = len(tasks)
        success = sum(1 for t in tasks.values() if t.get("status") == "success")
        summary = f"📊 任务统计: 成功 {success}/{total}\n\n" + summary
        
        return send_to_serverchan("📱 每日签到报告", summary)
    """
    """诊断测试版：完整输出 argv 所有字段内容"""
    def run(self, context: Context, argv) -> bool:
        task_name = argv.task_detail.entry  # 任务入口名  
        print(f"当前任务: {task_name}")  
        return True