# agent/config_loader.py
import json
from pathlib import Path

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