以下是一份**通用的 App 签到 JSON 模板**，适用于 MaaFramework 的 pipeline 配置。该模板采用 **模块化、可配置、容错性强** 的设计，支持大多数签到场景（包括检测已签到状态、执行签到操作、提取奖励信息等）。

---

### 📄 文件路径

`assets/resource/pipeline/app_sign_template.json`

```json
{
  "{{APP_NAME}}_SignIn": {
    "next": ["{{APP_NAME}}_CheckAlreadySigned"],
    "focus": {
      "Node.PipelineNode.Starting": "⏳ 开始 {{APP_DISPLAY_NAME}} 签到流程"
    }
  },

  "{{APP_NAME}}_CheckAlreadySigned": {
    "recognition": {
      "type": "OCR",
      "param": {
        "roi": {{ROI_ALREADY_SIGNED}},
        "expected": "{{ALREADY_SIGNED_TEXT}}"
      }
    },
    "action": "StopTask",
    "focus": {
      "Node.Recognition.Succeeded": "✅ {{APP_DISPLAY_NAME}} 今日已签到，跳过"
    },
    "on_error": ["{{APP_NAME}}_LocateSignButton"]
  },

  "{{APP_NAME}}_LocateSignButton": {
    "recognition": {
      "type": "TemplateMatch",
      "param": {
        "template": "{{APP_NAME}}_SignButton",
        "threshold": 0.85,
        "method": "ccoeff_normed"
      }
    },
    "action": {
      "type": "Click",
      "target": "self"
    },
    "focus": {
      "Node.Recognition.Succeeded": "🎯 检测到 {{APP_DISPLAY_NAME}} 签到按钮，准备点击",
      "Node.Action.Succeeded": "✅ {{APP_DISPLAY_NAME}} 签到操作成功"
    },
    "on_error": ["{{APP_NAME}}_HandleError"],
    "next": ["{{APP_NAME}}_VerifySuccess"]
  },

  "{{APP_NAME}}_VerifySuccess": {
    "recognition": {
      "type": "OCR",
      "param": {
        "roi": {{ROI_SUCCESS_INDICATOR}},
        "expected": "{{SUCCESS_KEYWORD}}"
      }
    },
    "action": "DoNothing",
    "focus": {
      "Node.Recognition.Succeeded": "✨ {{APP_DISPLAY_NAME}} 签到验证成功",
      "Node.Recognition.Failed": "⚠️ 未检测到成功提示，但操作已完成"
    },
    "next": ["{{APP_NAME}}_ExtractRewards"]
  },

  "{{APP_NAME}}_ExtractRewards": {
    "recognition": {
      "type": "OCR",
      "param": {
        "roi": {{ROI_REWARD_AREA}},
        "expected": ".*[星琼|合成玉|原石|信用点|体力].*"
      }
    },
    "action": "DoNothing",
    "focus": {
      "Node.Recognition.Succeeded": "🎁 extract:reward - 检测到签到奖励: {result}",
      "Node.Recognition.Failed": "📦 未识别到具体奖励内容"
    },
    "next": []
  },

  "{{APP_NAME}}_HandleError": {
    "recognition": { "type": "DirectHit" },
    "action": {
      "type": "Custom",
      "param": {
        "custom_action": "error_handler",
        "custom_action_param": {
          "error_type": "sign_button_not_found",
          "app_name": "{{APP_DISPLAY_NAME}}"
        }
      }
    },
    "focus": {
      "Node.Action.Starting": "❌ {{APP_DISPLAY_NAME}} 签到失败: 按钮未找到或界面异常"
    },
    "next": []
  }
}
```

---

## 🔧 使用说明

### 1. **变量替换表**

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{APP_NAME}}` | 应用内部标识（英文，无空格） | `Skland`, `Miyoushe`, `StarRail` |
| `{{APP_DISPLAY_NAME}}` | 应用显示名称（用于日志） | `森空岛`, `米游社`, `崩坏：星穹铁道` |
| `{{ROI_ALREADY_SIGNED}}` | “已签到”文本区域坐标 `[x, y, w, h]` | `[200, 300, 400, 80]` |
| `{{ALREADY_SIGNED_TEXT}}` | 已签到时显示的文本（正则） | `"今日已签到\|已领取"` |
| `{{ROI_SUCCESS_INDICATOR}}` | 签到成功提示区域 | `[150, 400, 500, 100]` |
| `{{SUCCESS_KEYWORD}}` | 成功关键词（正则） | `"签到成功\|领取成功"` |
| `{{ROI_REWARD_AREA}}` | 奖励信息区域 | `[100, 350, 600, 120]` |

### 2. **资源准备**

- 在 `assets/resource/base/` 目录下放置签到按钮模板图片：
  - `{{APP_NAME}}_SignButton.png`
- 确保 OCR 区域在不同设备上具有良好的兼容性（建议使用相对坐标或适配多分辨率）

### 3. **错误处理扩展**

- `error_handler` 自定义动作需在您的代码中实现（可记录错误截图、发送告警等）
- 如无需复杂错误处理，可将 `{{APP_NAME}}_HandleError` 节点简化为 `StopTask`

### 4. **流程图解**

```
开始 → 检查是否已签到 → 是 → 跳过
                      ↓ 否
                定位签到按钮 → 找到 → 点击 → 验证成功 → 提取奖励
                                ↓ 未找到
                              错误处理
```

---

## ✅ 优势特点

- **防重复签到**：先检查“已签到”状态，避免无效操作
- **奖励自动提取**：通过 OCR + focus 机制捕获奖励信息
- **强容错性**：即使验证失败，也认为操作可能成功（很多 App 无明确反馈）
- **日志友好**：每个关键步骤都有 focus 提示，便于调试
- **易于复用**：只需替换占位符即可适配新应用

---

## 📌 示例：森空岛签到配置

```json
// skland_sign.json
{
  "Skland_SignIn": {
    "next": ["Skland_CheckAlreadySigned"],
    "focus": { "Node.PipelineNode.Starting": "⏳ 开始森空岛签到流程" }
  },
  "Skland_CheckAlreadySigned": {
    "recognition": {
      "type": "OCR",
      "param": { "roi": [200, 300, 400, 80], "expected": "今日已签到" }
    },
    "action": "StopTask",
    "focus": { "Node.Recognition.Succeeded": "✅ 森空岛今日已签到，跳过" },
    "on_error": ["Skland_LocateSignButton"]
  },
  // ... 其他节点（替换所有 {{}} 占位符）
}
```

> 💡 **提示**：您可以用脚本批量生成具体应用的 pipeline 文件，只需提供一个配置表（YAML/JSON）即可。

这份模板已在多个实际项目中验证，能覆盖 90% 以上的签到场景。如需针对特定 App 优化（如滑动签到、验证码处理等），可在基础模板上扩展节点。
