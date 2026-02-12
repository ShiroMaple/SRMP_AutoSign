# agent/notifier.py
import json
from pathlib import Path
from serverchan_sdk import sc_send

CONFIG_DIR = Path("../assets/config")

def load_config(filename: str) -> dict:
    """安全加载配置文件，失败时返回空字典"""
    config_path = CONFIG_DIR / filename
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[!] 配置加载失败 {filename}: {e}")
    return {}

def send_to_serverchan(title: str, desp: str):
    options = {"tags": "MaaFw"}
    config = load_config("serverchan.json")
    sendkey = config.get("sendkey", "").strip()
    
    if not sendkey or sendkey == "your_send_key_here":
        print("[!] 未配置有效的 ServerChan3 SendKey，跳过推送")
        return False
    
    try:
        resp = sc_send(sendkey, title, desp, options)
        print("[✅]  ServerChan推送成功")
        return True
    except Exception as e:
        print(f"[❌] ServerChan推送异常: {e}")
        return False
    