# agent/report_manager.py
from pathlib import Path
import json
from notifier import send_to_serverchan
from datetime import datetime

def send_final_report(extra_content: str = ""):
    """生成并发送最终汇总报告（由 Client 端调用）"""
    state_file = Path("assets/config/sign_state.json")
    if not state_file.exists():
        print("[!] 状态文件不存在")
        return False
    
    state = json.loads(state_file.read_text())
    tasks = state.get("tasks", {})
    
    # 生成报告内容
    lines = ["# 📱 每日签到自动报告", f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    
    # 任务统计
    total = len(tasks)
    success = sum(1 for t in tasks.values() if t.get("success"))
    lines.append(f"## 📊 任务统计\n- 总任务数: {total}\n- 成功: {success}\n- 失败: {total - success}\n")
    
    # 详细列表
    lines.append("## 📋 任务详情")
    for name, info in sorted(tasks.items()):
        status = "✅ 成功" if info.get("success") else f"❌ 失败 (尝试{info.get('attempts',0)}次)"
        lines.append(f"- **{name}**: {status}")
        
        # 附加内容
        if info.get("contents"):
            for c in info["contents"]:
                lines.append(f"  - 🎁 {c['type']}: `{c['value']}` (节点: {c['node']})")
    
    # 附加提示
    if extra_content:
        lines.append(f"\n## 💡 附加提示\n{extra_content}")
    
    summary = "\n".join(lines)
    
    # 发送通知
    print("[📤] 报告预览:\n" + summary[:300] + "...")
    return send_to_serverchan("📱 每日签到报告", summary)