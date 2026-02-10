# 📌 MaaFramework 自动签到工具开发规范（Agent 模式）

> **目标**：基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 构建一个支持多 App 自动签到的个人工具，使用 **Agent 模式 + Pipeline 驱动**，Python 仅用于补充逻辑（如状态检查、日志、推送），核心流程由 JSON Pipeline 定义。

---

## 🔗 关键文档参考

- 官方 GitHub：<https://github.com/MaaXYZ/MaaFramework>  
- 中文文档：<https://maafw.com/docs/1.1-QuickStarted>  
- Agent 自定义动作：<https://maafw.com/docs/3.2-AgentCustomAction>  
- 回调协议：<https://maafw.com/docs/2.3-CallbackProtocol>  
- Server酱3 推送文档：<https://doc.sc3.ft07.com/zh/serverchan3>  

---

## 🗂️ 项目结构约定

```
SRMP_AutoSign/
├── agent/                     # Python 代码目录
│   ├── main.py                
│   ├── logger.py              # 日志与状态管理（按天 JSON 文件）
│   ├── notifier.py            # Server酱3 推送
│   ├── check_action.py        # 任务前检查（跳过/重试控制）
│   └── report.py              # 最终报告推送
├── assets/
│   ├── config/                # 配置文件（暂未使用）
│   ├── logs/                  # 自动生成：YYYY-MM-DD.json
│   └── resource/
│       ├── image/             # 图片资源
│       ├── model/             # OCR 模型等
│       └── pipeline/          # 各 App 签到流程（JSON）
│           ├── Skland.json
│           └── ...
└── assets/interface.json      # MaaFramework 的一个标准化的项目结构声明,包含指向各pipeline的入口任务列表
```

---

## ⚙️ 核心设计原则

### 1. **Pipeline 为主，Python 为辅**

- 所有签到步骤（点击、等待、OCR 识别等）**优先使用框架内置 Action**（如 `Click`, `KeyDown`, `DoNothing`）。
- 仅在必要时使用 `Custom` 节点调用 Python 补充功能（如状态检查、复杂逻辑）。

### 2. **每个任务必须包含 Init 节点**

- 每个 Pipeline 的第一个节点必须调用 `check_and_skip` Custom Action。
- 用于实现：
  - 跳过当日已成功任务
  - 控制最大重试次数（默认 2 次，即最多执行 3 次）
- 若需跳过，Custom Action 返回 `False`，框架自动终止当前任务。

### 3. **日志与状态持久化**

- 使用 **按日期命名的 JSON 文件** 存储签到状态：`assets/logs/YYYY-MM-DD.json`
- 文件结构：

  ```json
  {
    "date": "2026-02-10",
    "run_start": "ISO8601时间",
    "tasks": {
      "App名称": {
        "status": "success|failed",
        "attempts": 1,
        "end_time": "..."
      }
    }
  }
  ```

### 4. **最终报告推送**

- 在 `interface.json` 末尾添加 `"entry_send_report"` 任务。
- 由 `report_action.py` 读取当日日志，生成摘要并通过 Server酱3 推送。

---

## 🧩 关键组件说明

### ✅ `logger.py` —— 状态管理器

- **路径**：`agent/logger.py`
- **功能**：
  - `get_task_status(app_name)` → 获取是否成功、已尝试次数
  - `mark_success(app_name)` / `mark_failed(app_name)` → 更新状态
  - `get_summary()` → 生成推送文本
- **存储位置**：`assets/logs/YYYY-MM-DD.json`

> ✅ 已提供完整实现（见上文）

---

### ✅ `check_action.py` —— 任务前检查

- **注册名**：`check_and_skip`
- **调用方式**（在 Pipeline 中）：

  ```json
  {
    "action": {
      "type": "Custom",
      "param": {
        "custom_action": "check_and_skip",
        "app_name": "森空岛"
      }
    },
    "recognition": { "type": "DirectHit" }
  }
  ```

- **逻辑**：
  - 若今日已成功 → 返回 `False`（跳过）
  - 若重试次数 ≥ 2 → 返回 `False`（跳过）
  - 否则 → 返回 `True`（继续执行）

---

### ✅ `report.py` —— 报告推送

- **注册名**：`send_report`
- **调用方式**：作为 `interface.json` 的最后一个任务
- **功能**：读取当日日志 → 调用 `notifier.py` → 推送 Server酱3

---

### ✅ `notifier.py` —— 推送服务

- 通过环境变量 `SERVERCHAN_SENDKEY` 配置密钥
- 使用 `requests` 调用 Server酱3 API

---

## 📝 开发流程指引（给其他 Agents）

1. **新增一个 App 签到任务**：
   - 在 `assets/resource/pipeline/` 下创建 `YourApp.json`
   - 第一个节点必须是 `check_and_skip`，并传入 `app_name`
   - 后续节点使用标准 Action（Click / OCR / Wait 等）完成签到

2. **注册任务到入口**：
   - 编辑 `assets/interface.json`，在 `task` 列表中添加：

     ```json
     { "name": "你的App", "entry": "YourApp_Pipeline_Entry" }
     ```

3. **确保最后一个是报告任务**：

   ```json
   { "name": "推送报告", "entry": "entry_send_report" }
   ```

4. **测试与调试**：
   - 查看 `assets/logs/` 下的日志文件
   - 可手动删除当日日志以重新运行

---

## 🚫 注意事项

- **不要修改main.py，仅作为agent的启动入口**
- **常规的控制任务调度由MaaFramework自行完成，agent仅在必要时干预**：流程主要由 Pipeline 驱动。
- **不要硬编码 SendKey**：通过环境变量注入。
- **Custom Action 仅用于“决策”或“副作用”**，不要替代标准 Action。
- **Pipeline 节点命名清晰**，便于调试和维护。

---

## ✅ 附录：关键代码模板位置

| 功能 | 文件 |
|------|------|
| 日志管理 | [`agent/logger.py`](#✅-loggerpy--状态管理器) |
| 任务检查 | [`agent/check_action.py`](#✅-check_actionpy--任务前检查) |
| 报告推送 | [`agent/report.py`](#✅-reportpy--报告推送) |
| Server酱3 | [`agent/notifier.py`](#✅-notifierpy--推送服务) |

---

> 💡 **后续开发方向建议**：
>
> - 添加 Web UI 查看历史日志（可选）
> - 支持截图失败时自动保存（用于调试）
> - 增加“强制重试”开关（通过配置文件）

此文档可作为团队协作的基准规范，确保所有开发者对架构理解一致。
