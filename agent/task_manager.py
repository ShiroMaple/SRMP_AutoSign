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
            cls._instance.task_name_mapping = {}  # entry -> name 映射字典
            cls._instance._load_task_name_mapping()
        return cls._instance

    # 注册任务ID和入口名的映射
    def register_task_name(self, task_id: int, task_name: str):
        """任务开始时调用：记录 task_id 对应的 entry"""
        if task_name != "NotifyReport":  # 跳过报告任务
            self.task_id_to_name[task_id] = task_name
            #print(f"[📝] 注册任务映射: task_id={task_id} → {task_name}")
    
    # 通过 task_id 获取任务名
    def get_task_name_by_id(self, task_id: int) -> str:
        """优先查翻译本，查不到再推断（兜底）"""
        if task_id in self.task_id_to_name:
            return self.task_id_to_name[task_id]
        
        print(f"[⚠️] 未找到 task_id={task_id} 的映射！使用兜底推断")
        return f"Task_{task_id}"
    
    # 任务结束时清理（防内存泄漏）
    def unregister_task(self, task_id: int):
        self.task_id_to_name.pop(task_id, None)
    
    def _load_task_name_mapping(self):
        """从 interface.json 加载 task 的 entry -> name 映射"""
        try:
            interface_path = Path(__file__).parent.parent / "assets" / "interface.json"
            with open(interface_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 使用正则表达式提取 task 部分的 entry 和 name
            import re
            # 匹配两种顺序：entry 在前或 name 在前
            pattern1 = r'"entry":\s*"([^"]+)"\s*,\s*"name":\s*"([^"]+)"'
            pattern2 = r'"name":\s*"([^"]+)"\s*,\s*"entry":\s*"([^"]+)"'
            
            matches1 = re.findall(pattern1, content)
            matches2 = re.findall(pattern2, content)
            
            for entry, name in matches1:
                self.task_name_mapping[entry] = name
            for name, entry in matches2:
                self.task_name_mapping[entry] = name
            
            #print(f"[📋] 已加载 {len(self.task_name_mapping)} 个任务名称映射")
        except Exception as e:
            print(f"[⚠️] 加载任务名称映射失败: {e}")
    
    def _convert_task_name(self, task_name: str) -> str:
        """将 task_name 转换为显示名称，如果映射不存在则保留原值"""
        return self.task_name_mapping.get(task_name, task_name)    
    
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
        #print(f"[📊] 记录任务结果: {task_name} -> {'✅' if success else '❌'}")
    
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
            
            # 转换任务名称为显示名称
            display_name = self._convert_task_name(task_name)
            
            # 基础任务信息
            task_report = f"\n• {display_name}: {status}"
            
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
            print("[📦] 报告已成功发送到 ServerChan")
        else:
            print("[⚠️] 报告发送失败")
        
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
            print(f"[💾] 报告已保存至: assets/reports/{filename}")
        except Exception as e:
            print(f"[⚠️] 报告保存失败: {e}")