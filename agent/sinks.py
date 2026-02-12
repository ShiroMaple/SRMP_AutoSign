# agent/sinks.py
from maa.agent.agent_server import AgentServer
from maa.tasker import TaskerEventSink
from maa.context import ContextEventSink
from maa.event_sink import NotificationType
from task_manager import GlobalTaskManager

@AgentServer.tasker_sink()
class TaskStatusSink(TaskerEventSink):
    """任务状态监听器"""
    
    def on_tasker_task(self, tasker, noti_type: NotificationType, detail):
        task_name = detail.entry
        manager = GlobalTaskManager()
        
        if noti_type == NotificationType.Succeeded:
            # 排除 FinalReport 任务本身
            if task_name != "FinalReport":
                manager.record_task_result(task_name, True)
                print(f"[✅] 任务成功: {task_name}")
        
        elif noti_type == NotificationType.Failed:
            if task_name != "FinalReport":
                manager.record_task_result(task_name, False)
                print(f"[❌] 任务失败: {task_name}")

@AgentServer.context_sink()
class FinalReportSink(ContextEventSink):
    """结束任务监听器"""
    
    def on_node_pipeline_node(self, context, noti_type: NotificationType, detail):
        # 监听 FinalReport 任务的完成事件
        if detail.name == "NotifyReport" and noti_type == NotificationType.Succeeded:
            print("[✨] 检测到 NotifyReport 任务，准备发送全局报告...")
            GlobalTaskManager().send_final_report()