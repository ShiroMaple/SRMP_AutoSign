# agent/notifier.py
from config_loader import load_config
from serverchan_sdk import sc_send

def send_to_serverchan(title: str, desp: str):
    options = {"tags": "MaaFw"}
    config = load_config("serverchan.json")
    sendkey = config.get("sendkey", "").strip()
    
    if not sendkey or sendkey == "your_send_key_here":
        print("[!] 未配置有效的 ServerChan3 SendKey，跳过推送")
        return False
    
    try:
        resp = sc_send(sendkey, title, desp, options)
        if resp.status_code == 200:
            print("[✓] ServerChan推送成功")
            return True
        else:
            print(f"[✗] ServerChan推送失败: {resp.text}")
            return False
    except Exception as e:
        print(f"[✗] ServerChan推送异常: {e}")
        return False
    