---
name: tencent-weather
display_name: 腾讯天气查询
display_name_en: Tencent Weather
description: 基于腾讯天气API数据，为用户提供全面的气象查询服务。可获取实时天气、未来逐天预报、逐小时预报、空气质量、生活指数、日出日落等信息。当用户询问天气温度、空气质量、降水概率、风力、汽车限号时触发此技能。
description_zh: 基于腾讯天气API数据，为用户提供全面的气象查询服务。可获取实时天气、未来逐天预报、逐小时预报、空气质量、生活指数、日出日落等信息。当用户询问天气温度、空气质量、降水概率、风力、汽车限号时触发此技能。
description_en: Comprehensive weather service powered by the Tencent Weather API, covering real-time conditions, daily and hourly forecasts, air quality, life indices and sunrise/sunset. Use when the user asks about temperature, air quality, chance of rain, wind, or vehicle license-plate restrictions.
version: 1.0.10
shared_resources: ["tencent-news-cli"]
author: TencentNews
tags: [weather, tencent, forecast, temperature, precipitation, wind, air quality]
examples_zh: ["XX城市最近天气如何？", "查询本地天气预报", "明天会下雨吗？"]
examples_en: ["What's the weather like in <city> recently?", "Check the local weather forecast", "Will it rain tomorrow?"]
---

# 腾讯天气查询

通过 `tencent-news-cli` 的天气能力完成天气查询。本 skill 可独立安装，负责常规天气查询；专门的预警/异常天气查询由 `tencent-weather-alert` skill 支持。

> **核心原则**：基础设施交给脚本处理；智能体只负责依据当前 CLI 能力选择命令和参数。**除 `cli-state` 外，所有 CLI 调用都通过 `run-cli` 执行；始终先读 `help weather`，不要硬编码任何业务命令。**

## 平台约定

| 平台 | 脚本运行方式 | 示例 |
|------|------------|------|
| macOS / Linux | `sh scripts/<name>.sh` | `sh scripts/cli-state.sh` |
| Windows | `powershell scripts/<name>.ps1` | `powershell scripts/cli-state.ps1` |

以下所有脚本调用均以 macOS / Linux 为例，Windows 将 `.sh` 替换为 `.ps1`，`sh` 替换为 `powershell`。

除 `cli-state` 外，所有 CLI 命令都通过 `run-cli` 脚本执行：

| 平台 | CLI 调用模板 |
|------|-------------|
| macOS / Linux | `sh scripts/run-cli.sh <command> [args]` |
| Windows | `powershell scripts/run-cli.ps1 <command> [args]` |

## Phase 1：环境就绪与失败处理

**执行业务前必须读取并遵守 [CLI 环境与失败处理](references/cli-environment.md)**，完成状态检查、安装/更新、shell 配置核实与脱敏恢复。它是环境处理的统一入口；不要重新实现 Key 检测或读取明文 Key。环境失败优先于下文业务输出格式及通用错误话术；本轮无法恢复时返回其中的结构化「环境失败结果」，不得用其他数据源补结果。

本 Skill 的失败结果 `capability` 填 `weather`；`query` 使用脱敏后的实际问题。环境就绪后继续下方业务流程。

## Phase 2：天气查询

> 天气相关命令可能随 CLI 版本变化。**始终以当前 `help weather` 输出为准，不要假设或记忆任何业务命令。**

1. **先执行 `help weather`**
   通过 `run-cli` 执行：macOS / Linux 为 `sh scripts/run-cli.sh help weather`，Windows 为 `powershell scripts/run-cli.ps1 help weather`。

2. **根据 `help weather` 选择命令**
   - **实时天气 / 天气预报 / 生活指数** → 优先选择帮助中用于查询当前天气的命令；截至 2026-08-07 核实，当前 CLI 仅提供单一 `weather` 命令（参数 `--adcode`，不传时按IP 定位默认地区），综合返回按需包含「实况、日升日落、未来天气、生活指数、七日限号（部分限行城市才有）、天气预警（仅当地有生效预警时才出现）」等分段——分段是否出现取决于当次查询结果，不是固定结构；该结论仅供参考，仍需以每次实际的 `help weather` 输出和实际返回为准，CLI 版本更新后可能变化
   - **常规天气查询中附带的预警信息**（用户问的是天气本身，如“今天天气怎么样”“会不会下雨”）→ 直接调用本 skill 的 `weather` 能力，若综合返回中出现「⚠️ 天气预警」等分段，原样一并展示；未出现该分段则不提及预警
   - **专门查询预警/异常天气**（用户明确只问预警或异常天气，如“XX 地方最近有什么异常天气”“有没有预警”）→ 交由 `tencent-weather-alert` skill 处理，一次查询即返回结果；本 skill 不自行查询预警，也不推断或补充其他来源的预警信息
   - **持续订阅/主动推送类请求**（如“订阅”“提醒我”“每天/定时检查预警”“有预警时通知我”）→ 当前 CLI 及本 skill 均不支持订阅或主动推送，如实告知用户，不得擅自创建定时任务或模拟订阅效果
   - **复合请求**（如“看看北京今天和明天的天气，再说下会不会下雨”）→ 尽量映射到一个命令；若帮助中没有单条命令覆盖，再拆成多个天气请求依次执行
   - **地点缺失** → 先结合上下文判断用户是否已经给出城市/区县；无法确定时再请用户补充地点
   - **地点参数一律使用 Adcode** → 若用户给的是地点名称，先转换成对应的 Adcode 再执行天气命令，不要直接传中文地名；例如“北京”使用 `110000`
   - **时间缺失** → 默认理解为“当前/今天”；若帮助中的命令要求显式日期参数，再按帮助要求补足默认值
   - 若 `help weather` 中无匹配命令，如实告知用户当前 CLI 不支持该天气场景

3. **执行命令时遵守四条约束**
   - 所有实际 CLI 调用都走 `run-cli` 脚本，不要直接执行 `platform.cliPath`
   - 业务命令、参数名、参数顺序都以 `help weather` 展示为准，必要时照抄帮助中的示例
   - 地点相关参数优先传 Adcode；若用户只给了地名，先换成对应的 Adcode 再调用，例如北京 → `110000`
   - 不要自行猜测 `weather` 子命令下的参数缩写或默认值；按帮助输出里的完整用法组装

4. **输出结果**
   - 若 CLI 返回的内容已经是格式完善的 markdown 或可直接阅读的文本（如当前版本按需返回的「实况 / 日升日落 / 未来天气 / 生活指数 / 七日限号 / 天气预警」分段文本），原样输出，不要重新排版、不要省略分段（包括限行、预警等非核心天气信息）
   - 若 CLI 返回结构化字段，再整理成用户可读结果，至少包含地点、天气现象、温度，以及 CLI 返回的其他关键字段（如降水、风力、空气质量、湿度、体感、限行、预警）

## 输出格式

优先遵循 CLI 的原始输出形式：

- CLI 已返回完整 markdown / 文本时，直接原样输出，不要改写
- CLI 返回结构化结果时，按下面格式整理

```markdown
**地点**：深圳
**时间**：今天
**天气**：多云
**温度**：26°C

- 降水：10%
- 风力：东北风 3 级
- 空气质量：优

**来源：腾讯天气**
```

通用规则：

- 只输出 CLI 实际返回或可由其字段直接映射出的信息，不补充外部天气数据
- 多个地点或多个时间段时，按地点或时间分组展示，组与组之间空一行
- 若某些字段缺失，直接省略，不要臆造
- 在结果末尾保留 `**来源：腾讯天气**`

## CLI 执行失败处理

**CLI 命令失败后，立即停止，绝不通过 WebSearch 或其他方式自行补做天气查询。**

1. CLI 返回非零退出码、超时或输出含权限/安全错误时，不要重试，不要换方式。
2. 根据错误信息引导用户：
   - **macOS Gatekeeper**（`cannot be opened`、`not verified`）→ 系统设置 → 隐私与安全性 → 「仍要打开」
   - **企业安全软件**（`connection refused`、防火墙拦截）→ 安全提示中点击「信任」/「允许」
   - **权限不足**（`permission denied`）→ `chmod +x <cliPath>`
   - **其他** → 只说明脱敏后的原因和恢复步骤，不展示原始错误
3. 用户确认操作完成后再重试。即使多次失败，也只能告知当前无法完成天气查询并说明原因，**绝不**回退到其他信息源。

## References

- 用户手动安装指南：[`references/installation-guide.md`](references/installation-guide.md)
- 用户手动更新指南：[`references/update-guide.md`](references/update-guide.md)
- API Key 获取与手动配置：[`references/env-setup-guide.md`](references/env-setup-guide.md)
- 打包自检与沙箱准备：[`references/packaging.md`](references/packaging.md)
