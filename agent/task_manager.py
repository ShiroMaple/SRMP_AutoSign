# agent/task_manager.py
from pathlib import Path
from datetime import datetime
from logger import SignInLogger
import json

class GlobalTaskManager:
    """全局任务管理器，用于收集所有任务结果并生成最终报告"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = SignInLogger()
            cls._instance.task_results = {}  # {task_name: result}
            cls._instance.extracted_contents = {}  # {task_name: {key: value}}
            cls._instance.focus_messages = {}  # {task_name: [messages]}
            cls._instance.task_id_to_name = {}  # 翻译本：task_id → task_name
        return cls._instance

    # 注册任务ID和入口名的映射
    def register_task_name(self, task_id: int, task_name: str):
        """任务开始时调用：记录 task_id 对应的 entry"""
        if task_name != "NotifyReport":  # 跳过报告任务
            self.task_id_to_name[task_id] = task_name
            print(f"[📝] 注册任务映射: task_id={task_id} → {task_name}")
    
    # 通过 task_id 获取任务名（精准！）
    def get_task_name_by_id(self, task_id: int) -> str:
        """优先查翻译本，查不到再推断（兜底）"""
        if task_id in self.task_id_to_name:
            return self.task_id_to_name[task_id]
        
        # 兜底方案（理论上不应触发）
        print(f"[⚠️] 未找到 task_id={task_id} 的映射！使用兜底推断")
        return f"Task_{task_id}"
    
    # 任务结束时清理（防内存泄漏）
    def unregister_task(self, task_id: int):
        self.task_id_to_name.pop(task_id, None)    
    
    def _ensure_task_exists(self, task_name: str):
        """确保存在任务记录条目"""
        if task_name not in self.task_results:
            self.task_results[task_name] = {
                "success": None,  # 初始状态未知
                "timestamp": datetime.now().isoformat(),
                "focus_messages": [],
                "extracts": {}
            }
    
    def record_task_result(self, task_name: str, success: bool):
        """记录单个任务结果"""
        self._ensure_task_exists(task_name)
        self.task_results[task_name]["success"] = success
        print(f"[📊] 记录任务结果: {task_name} -> {'✅' if success else '❌'}")
    
    def record_focus_message(self, task_name: str, message: str):
        """记录任务的 focus 消息"""
        self._ensure_task_exists(task_name)
        
        # 避免重复记录
        if message not in self.task_results[task_name]["focus_messages"]:
            self.task_results[task_name]["focus_messages"].append(message)
            # 同时保存到专用存储（可选）
            if task_name not in self.focus_messages:
                self.focus_messages[task_name] = []
            self.focus_messages[task_name].append(message)
    
    def record_extracted_content(self, task_name: str, key: str, value: str):
        """记录提取的结构化内容"""
        self._ensure_task_exists(task_name)
        
        # 初始化提取字典
        if "extracts" not in self.task_results[task_name]:
            self.task_results[task_name]["extracts"] = {}
        
        # 保存提取内容
        self.task_results[task_name]["extracts"][key] = value
        
        # 同时保存到专用存储（便于后续使用）
        if task_name not in self.extracted_contents:
            self.extracted_contents[task_name] = {}
        self.extracted_contents[task_name][key] = value
    
    def generate_final_report(self) -> str:
        """生成最终全局报告（增强版：包含focus和提取内容）"""
        print("正在生成全局报告...")
        total = len(self.task_results)
        success_count = sum(1 for r in self.task_results.values() 
                          if r.get("success") is True)
        
        report_lines = [
            f"\n📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n🎯 总任务数: {total} ",
            f"✅ 成功: {success_count} ",
            f"❌ 失败: {total - success_count} ",
            "\n📋 详细结果:"
        ]
        
        for task_name, result in self.task_results.items():
            status = "✅" if result.get("success") is True else "❌" if result.get("success") is False else "⏳"
            
            # 基础任务信息
            task_report = f"\n• {task_name}: {status}"
            
            # 添加提取内容（如果有）
            extracts = result.get("extracts", {})
            if extracts:
                extract_strs = [f"{k}: {v}" for k, v in extracts.items()]
                task_report += ""
                task_report += f"\n  └─ 提取内容: {', '.join(extract_strs)}"
            
            # 添加关键 focus 消息（简化显示）
            focus_msgs = result.get("focus_messages", [])
            # 只显示包含错误或关键信息的消息
            important_msgs = [m for m in focus_msgs 
                            if "error" in m.lower() or "fail" in m.lower() or "extract" in m.lower()]
            
            if important_msgs:
                task_report += ""
                task_report += f"\n  └─ 关键消息: {important_msgs[0]}"
                if len(important_msgs) > 1:
                    task_report += f" (+{len(important_msgs)-1} 更多)"
            
            report_lines.append(task_report)
        
        return "\n".join(report_lines)
    
    def send_final_report(self):
        """发送报告到 ServerChan"""
        from notifier import send_to_serverchan
        
        report = self.generate_final_report()
        print("\n" + "="*50)
        print(report)
        print("="*50 + "\n")
        #为符合serverchan要求的Markdown格式，将所有\n替换为\n\n
        report =report.replace('\n', '\n\n') 
        
        success = send_to_serverchan("✅ SRMP_AutoSign 执行完成", report)
        if success:
            print("[📦] 全局报告已成功发送到 ServerChan")
        else:
            print("[⚠️] 全局报告发送失败")
        
        # 保存完整报告到文件（可选）
        self._save_full_report(report)
        
        # 清空本次执行的结果（为下次运行准备）
        self.task_results.clear()
        self.extracted_contents.clear()
        self.focus_messages.clear()
    
    def _save_full_report(self, report: str):
        """保存完整报告到文件（调试用）"""
        try:
            report_dir = Path(__file__).parent.parent / "assets" / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_dir / filename, "w", encoding="utf-8") as f:
                # 写入完整任务数据（JSON格式）
                json.dump({
                    "summary": report,
                    "raw_data": self.task_results,
                    "extracted_contents": self.extracted_contents,
                    "focus_messages": self.focus_messages
                }, f, ensure_ascii=False, indent=2)
            print(f"[💾] 完整报告已保存至: assets/reports/{filename}")
        except Exception as e:
            print(f"[⚠️] 保存完整报告失败: {e}")