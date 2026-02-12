# agent/task_manager.py
from pathlib import Path
from datetime import datetime
from logger import SignInLogger

class GlobalTaskManager:
    """全局任务管理器，用于收集所有任务结果并生成最终报告"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = SignInLogger()
            cls._instance.task_results = {}  # {task_name: result}
        return cls._instance
    
    def record_task_result(self, task_name: str, success: bool):
        """记录单个任务结果"""
        self.task_results[task_name] = {
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        #print(f"[📊] 记录任务结果: {task_name} -> {'✅' if success else '❌'}")
    
    def generate_final_report(self) -> str:
        """生成最终全局报告"""
        total = len(self.task_results)
        success_count = sum(1 for r in self.task_results.values() if r["success"])
        
        report_lines = [
            f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"🎯 总任务数: {total}",
            f"✅ 成功: {success_count}",
            f"❌ 失败: {total - success_count}",
            "",
            "📋 详细结果:"
        ]
        
        for task_name, result in self.task_results.items():
            status = "✅" if result["success"] else "❌"
            report_lines.append(f"\n• {task_name}: {status}")
        
        return "\n".join(report_lines)
    
    def send_final_report(self):
        """发送最终报告到 ServerChan"""
        from notifier import send_to_serverchan
        
        report = self.generate_final_report()
        success = send_to_serverchan("📦 MaaFramework 全局任务完成", report)
        
        if success:
            #print("[📤] 全局报告已成功发送到 ServerChan")
            True
        else:
            print("[⚠️] 全局报告发送失败")
        
        # 清空本次执行的结果（为下次运行准备）
        self.task_results.clear()