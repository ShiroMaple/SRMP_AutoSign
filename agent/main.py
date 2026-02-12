# agent/main.py
from maa.toolkit import Toolkit
from maa.agent.agent_server import AgentServer
import sys
import my_reco
import my_action
# 导入 sinks 以注册回调
from sinks import TaskStatusSink, FinalReportSink

def main():
    Toolkit.init_option("./")
    if len(sys.argv) < 2:
        print("Usage: python main.py <socket_id>")
        print("socket_id is provided by AgentIdentifier.")
        sys.exit(1)
    
    socket_id = sys.argv[-1]
    success = AgentServer.start_up(socket_id)
    
    if success:
        print("\n--- MaaFramework 启动! ---")
        print("--- 状态管理器已激活，监听框架回调 ---")
        AgentServer.join()
        AgentServer.shut_down()

if __name__ == "__main__":
    main()