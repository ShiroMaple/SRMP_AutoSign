# agent/logger.py
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any
import threading

# 日志目录（相对于 agent/ 的上一级）
LOG_DIR = Path(__file__).parent.parent / "assets" / "logs"
LOCK = threading.Lock()  # 用于内存操作的线程锁（文件 I/O 本身加 fcntl 锁更佳，但为跨平台简化）

def _get_log_path() -> Path:
    """获取今日日志文件路径"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f"{date.today()}.json"

def _load_log() -> Dict[str, Any]:
    """加载今日日志，若不存在则返回空模板"""
    log_file = _get_log_path()
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "date": str(date.today()),
        "run_start": datetime.now().isoformat(),
        "tasks": {}
    }

def _save_log(data: Dict[str, Any]):
    """保存日志到文件"""
    log_file = _get_log_path()
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class SignInLogger:
    def __init__(self):
        self._cache = None  # 缓存日志内容，减少文件读取

    def _ensure_cache(self):
        if self._cache is None:
            self._cache = _load_log()

    def get_task_status(self, app_name: str) -> Dict[str, Any]:
        """
        获取某 App 的今日签到状态
        返回: {"success": bool, "attempts": int}
        """
        with LOCK:
            self._ensure_cache()
            task = self._cache["tasks"].get(app_name, {})
            return {
                "success": task.get("status") == "success",
                "attempts": task.get("attempts", 0)
            }

    def mark_success(self, app_name: str):
        """标记某 App 签到成功"""
        with LOCK:
            self._ensure_cache()
            self._cache["tasks"][app_name] = {
                "status": "success",
                "attempts": self._cache["tasks"].get(app_name, {}).get("attempts", 0),
                "end_time": datetime.now().isoformat()
            }
            _save_log(self._cache)

    def mark_failed(self, app_name: str):
        """标记某 App 签到失败，并增加尝试次数"""
        with LOCK:
            self._ensure_cache()
            prev = self._cache["tasks"].get(app_name, {})
            attempts = prev.get("attempts", 0) + 1
            self._cache["tasks"][app_name] = {
                "status": "failed",
                "attempts": attempts,
                "end_time": datetime.now().isoformat()
            }
            _save_log(self._cache)
        
    def add_task_content(self, app_name: str, content_type: str, content: str):
        """添加任务特定内容（如兑换码）"""
        with LOCK:
            self._ensure_cache()
            task = self._cache["tasks"].setdefault(app_name, {})
            task.setdefault("contents", []).append({
                "type": content_type,
                "content": content,
                "time": datetime.now().isoformat()
            })
            _save_log(self._cache)    

    def get_summary(self) -> str:
        """增强版摘要，包含额外内容"""
        with LOCK:
            self._ensure_cache()
            tasks = self._cache["tasks"]
            total = len(tasks)
            success = sum(1 for t in tasks.values() if t.get("status") == "success")
            failed = total - success
            
            summary = f"📅 {self._cache['date']} 自动签到报告\n✅ 成功: {success}\n❌ 失败: {failed}\n"
            
            # 添加兑换码等内容
            has_contents = False
            for app_name, task in tasks.items():
                contents = task.get("contents", [])
                if contents:
                    if not has_contents:
                        summary += "\n🎁 特别内容:\n"
                        has_contents = True
                    summary += f"\n{app_name}:\n"
                    for item in contents:
                        summary += f"  • [{item['type']}] {item['content']}\n"
            
            if failed > 0:
                failed_names = [name for name, t in tasks.items() if t.get("status") == "failed"]
                summary += f"\n⚠️ 失败应用: {', '.join(failed_names)}"
            
            return summary.strip()