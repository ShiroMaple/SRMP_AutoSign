import sys  
import os  
from pathlib import Path  
  
# 设置环境变量  
if len(sys.argv) >= 3:  
    install_dir = Path(sys.argv[2])  
    os.environ["MAAFW_BINARY_PATH"] = str(install_dir / "bin")  
  
# 添加binding路径  
if len(sys.argv) >= 2:  
    binding_dir = Path(sys.argv[1])  
    if str(binding_dir) not in sys.path:  
        sys.path.insert(0, str(binding_dir))  
  
from maa.agent.agent_server import AgentServer  
from maa.tasker import TaskerEventSink  
from maa.context import ContextEventSink  
from maa.event_sink import NotificationType  
  
@AgentServer.tasker_sink()  
class MyTaskerSink(TaskerEventSink):  
    def on_tasker_task(self, tasker, noti_type: NotificationType, detail):  
        print(f"[任务] {detail.entry} -> {noti_type.name}")  
  
@AgentServer.context_sink()  
class MyContextSink(ContextEventSink):  
    def on_raw_notification(self, context, msg: str, details: dict):  
        if msg.startswith("Node."):  
            print(f"[节点] {msg}")  
  
def main():  
    if len(sys.argv) < 2:  
        print("需要socket_id参数")  
        return  
      
    socket_id = sys.argv[-1]  
    print(f"Callback Agent 启动，socket_id: {socket_id}")  
      
    AgentServer.start_up(socket_id)  
    AgentServer.join()  
    AgentServer.shut_down()  
  
if __name__ == "__main__":  
    main()