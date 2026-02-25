# agent/sinks.py
from maa.agent.agent_server import AgentServer
from maa.tasker import TaskerEventSink
from maa.context import Context,ContextEventSink
from maa.event_sink import NotificationType
from task_manager import GlobalTaskManager
import re

@AgentServer.tasker_sink()
class TaskStatusSink(TaskerEventSink):
    """任务状态监听器 - 保持原有功能"""
    def on_tasker_task(self, tasker, noti_type: NotificationType, detail):
        manager = GlobalTaskManager()

        #任务开始时注册映射
        if noti_type == NotificationType.Starting:
            if detail.entry != "NotifyReport":
                manager.register_task_name(detail.task_id, detail.entry)
                display_name = manager._convert_task_name(detail.entry)
                print(f"[🚀] 任务开始: {display_name}")

        # 任务成功/失败输出并清理
        elif noti_type in [NotificationType.Succeeded, NotificationType.Failed]:
            if detail.entry != "NotifyReport":
                status = "完成" if noti_type == NotificationType.Succeeded else "失败"
                display_name = manager._convert_task_name(detail.entry)
                icon = "☑️" if noti_type == NotificationType.Succeeded else "❌"
                print(f"[{icon}] 任务{status}: {display_name}")
                manager.record_task_result(detail.entry, noti_type == NotificationType.Succeeded)
                manager.unregister_task(detail.task_id)

@AgentServer.context_sink()
class FocusContentSink(ContextEventSink):
    """
    专注内容监听器 - 修正版：直接处理原始回调中的 focus 消息
    工作原理：
    1. 框架在特定节点阶段触发回调（如 Node.Recognition.Succeeded）
    2. 从 details["focus"] 获取配置的模板
    3. 用 details 中的值替换 {placeholder}
    4. 输出到终端并保存到任务结果
    """
    
    def on_raw_notification(self, context:Context, msg: str, details: dict):
        """原始回调处理器 - 捕获所有消息"""
        # 跳过 NotifyReport 任务本身的 focus 消息
        if details.get("name", "").startswith("NotifyReport"):
            return
        
        # 从 details 拿 task_id（节点广播自带！）
        task_id = details.get("task_id")
        if task_id is None:
            print(f"[⚠️] 未查询到Focus消息所属的task_id: {msg}")
            return
        task_name = GlobalTaskManager().get_task_name_by_id(task_id)
        display_name = GlobalTaskManager()._convert_task_name(task_name)
                
        # 1. 检查是否存在 focus 数据
        focus_data = details.get("focus")
        if not focus_data:
            return
        
        # 2. 检查当前消息类型是否有对应的 focus 模板
        if not isinstance(focus_data, dict) or msg not in focus_data:
            return
        
        # 3. 获取模板并替换占位符
        template = focus_data[msg]
        try:
            # 添加 name 到 details 中，使用转换后的显示名称
            format_details = details.copy()
            format_details["name"] = display_name
            # 安全替换占位符（避免 KeyError）
            formatted_msg = template.format(**format_details)
        except KeyError as e:
            formatted_msg = f"[格式错误] 模板 '{template}' 缺少字段: {e}"
            print(f"[⚠️] Focus 消息格式错误: {formatted_msg}")
        
        # 4. 终端输出
        noti_type = self._notification_type(msg)
        status_emoji = "📝" if noti_type == NotificationType.Starting else "✅" if noti_type == NotificationType.Succeeded else "❌"
        print(f"[{status_emoji}] {display_name} > {formatted_msg}")
        
        # 5. 保存到任务结果
        GlobalTaskManager().record_focus_message(task_name, formatted_msg)
        
        # 6. 特殊处理：extract 消息（格式: "extract:key - value"）
        if "extract:" in formatted_msg:
            self._handle_extract_message(task_name, formatted_msg)
    
    def _handle_extract_message(self, task_name: str, message: str):
        """处理 extract 消息，提取结构化数据
        支持格式:
        - "extract:reward - 星琼×60"
        - "extract:status=已签到"
        - "extract:result:success"
        """
        # 统一格式: 提取 key 和 value
        patterns = [
            r'extract:(\w+)\s*-\s*(.+)',    # 格式1: key - value
            r'extract:(\w+)=(.+)',          # 格式2: key=value
            r'extract:(\w+):(.+)'           # 格式3: key:value
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                # 保存到任务的提取内容
                GlobalTaskManager().record_extracted_content(task_name, key, value)
                display_name = GlobalTaskManager()._convert_task_name(task_name)
                print(f"[📦] 已提取 {display_name} 的 {key}: {value}")
                return
        
        # 未匹配到标准格式，但包含 extract 关键字
        print(f"[🔍] 未解析 extract 消息: {message}")

@AgentServer.context_sink()
class FinalReportSink(ContextEventSink):
    """结束任务监听器 - 修正节点名称"""
    def on_node_pipeline_node(self, context:Context, noti_type: NotificationType, detail):
        # 监听 NotifyReport 任务的完成事件（修正节点名）
        if detail.name == "NotifyReport" and noti_type == NotificationType.Succeeded:
            print("[✨] 检测到 NotifyReport 任务，准备推送通知...")
            GlobalTaskManager().send_final_report()