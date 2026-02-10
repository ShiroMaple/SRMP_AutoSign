# notifier.py
import requests
#from config import SERVERCHAN_SENDKEY

#serverchan params
sendkey = "sctp2102ta-lbduuk43fh2pz462ln61oko4"
title = "SRMP_AutoSign"
options = {"tags": "MaaFw"}

def send_to_serverchan(title: str, content: str):
    if not SERVERCHAN_SENDKEY or SERVERCHAN_SENDKEY == "your_send_key_here":
        print("[!] 未配置 Server酱3 SendKey，跳过推送")
        return
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("[✓] ServerChan推送成功")
        else:
            print(f"[✗] ServerChan推送失败: {resp.text}")
    except Exception as e:
        print(f"[✗] ServerChan推送异常: {e}")