---
name: tencent-weather-alert
display_name: 腾讯天气预警
display_name_en: Tencent Weather Alerts
description: 基于腾讯天气预警API的气象数据提供查询服务，覆盖雨雪、雾霾、空气质量、寒潮、高温和台风等预警。当用户查询某地天气预警或最近有什么异常天气时使用该技能
description_zh: 基于腾讯天气预警API的气象数据提供查询服务，覆盖雨雪、雾霾、空气质量、寒潮、高温和台风等预警。当用户查询某地天气预警或最近有什么异常天气时使用该技能
description_en: Tencent weather alert / abnormal weather lookup tool for Chinese locations, covering rain, snow, haze, air quality, cold wave, high temperature, and typhoon alerts. One-off query only, no subscription or proactive push.
version: 2.0.4
shared_resources: ["tencent-news-cli"]
author: TencentNews
tags: [weather, weather alert, tencent, warning, rain, snow, haze, air quality, cold wave, heatwave, typhoon]
examples_zh: ["XX城市最近有寒潮预警吗？", "查询本地天气预警", "今天哪里有台风警报？"]
examples_en: ["Are there any cold wave alerts in <city> recently?", "Check local weather alerts", "Where are typhoon alerts in effect today?"]
---

# 腾讯天气预警

通过 `tencent-news-cli` 当前提供的天气能力查询某地的天气预警/异常天气，一次查询、一次返回。

> **核心原则**：本skill 只做“用户问一次、查一次、答一次”的即时查询，**不提供预警订阅、定时检查或主动推送等能力**；不固化 CLI 的子命令、参数、数据结构或版本行为，每次执行都先动态读取 CLI 帮助，再按当次实际暴露的能力调用。除 `cli-state` 外，所有 CLI 调用都通过 `run-cli` 执行。与腾讯新闻 skill 保持一致：单次意图仅调用必要能力一次；CLI 失败、超时或返回空结果时立即停止，不重试、不调用替代数据源。

## 平台约定

| 平台 | 脚本运行方式 | 示例 |
|------|------------|------|
| macOS / Linux | `sh scripts/<name>.sh` | `sh scripts/cli-state.sh` |
| Windows | `powershell scripts/<name>.ps1` | `powershell scripts/cli-state.ps1` |

以下示例以 macOS / Linux 为例；Windows 将 `.sh` 替换为 `.ps1`，`sh` 替换为 `powershell`。

除 `cli-state` 外，所有 CLI 命令都使用：

| 平台 | CLI 调用模板 |
|------|-------------|
| macOS / Linux | `sh scripts/run-cli.sh <command> [args]` |
| Windows | `powershell scripts/run-cli.ps1 <command> [args]` |

## Phase 1：环境就绪与失败处理

**执行业务前必须读取并遵守 [CLI 环境与失败处理](references/cli-environment.md)**，完成状态检查、安装/更新、shell 配置核实与脱敏恢复。它是环境处理的统一入口；不要重新实现 Key 检测或读取明文 Key。环境失败优先于下文业务输出格式及通用错误话术；本轮无法恢复时返回其中的结构化「环境失败结果」，不得用其他数据源补结果。

本 Skill 的失败结果 `capability` 填 `weather-alert`；`query` 使用脱敏后的实际问题。环境就绪后继续下方业务流程。

## Phase 2：动态发现并查询预警/异常天气

### 1. 动态发现能力

每次预警查询按下列顺序执行，不根据此前测试、历史帮助或本 skill 中的示例猜测命令：

1. 执行 `sh scripts/run-cli.sh help`，从**当前输出**中定位名称或说明与天气、气象、预警、灾害天气相关的可用命令。
2. 对选中的天气命令执行 `sh scripts/run-cli.sh help <天气命令>`，读取其真实用法、可选参数、地点输入方式和示例。
3. 只有帮助明确显示可以进一步查看预警子命令或预警参数时，才继续按帮助所示路径读取下一层帮助；未显示的子命令、参数和值都不得尝试。
4. 若当前 CLI 没有可用于天气预警或综合天气结果的能力，直接说明“当前 CLI 版本未提供天气预警查询能力”，不进行探测性调用。

> 截至 2026-08-14 核实（CLI v1.0.15）：无独立预警子命令或参数，仅有统一的 `weather --adcode` 命令（不传 `--adcode` 时按 IP 定位默认地区）；**预警信息包含在 `weather` 综合返回中**，仅当查询地点当前存在生效预警时，返回文本才会出现独立分段（如「⚠️ 天气预警」），每条预警包含颜色等级、预警编号+类型、发布单位与时间、正文内容、信息来源；若该地点当前无生效预警，则不会出现该分段。该结论仅供参考，CLI 版本更新后可能变化，**每次执行仍必须按上述步骤重新读取帮助**，不得跳过发现流程直接调用 `weather`，也不得因为某次查询没有预警分段就认为 CLI 不支持预警能力。

### 2. 识别用户关注的预警/异常天气类型

将用户诉求归入以下类型，用于从 CLI 实际返回结果中筛选或匹配；类型本身**不是** CLI 参数，除非当前帮助明确提供对应参数和值：

| 类型 | 匹配范围 |
|------|----------|
| 雨天 | 中雨、大雨、暴雨、大暴雨、特大暴雨、雷阵雨伴有冰雹、雨夹雪 |
| 雪天 | 小雪、中雪、大雪、暴雪 |
| 雾霾 | 沙尘暴、强沙尘暴、扬沙、霾、强浓度、中度霾、重度霾、严重霾、特强浓雾 |
| 空气质量 | AQI 重度污染预警 |
| 寒潮 | 大幅降温 |
| 高温 | 38°C 高温 |
| 台风 | 台风路径及影响 |

用户笼统询问“最近有什么异常天气”时，不预设类型，直接查询并展示 CLI 实际返回的全部预警/异常天气信息。

### 3. 组装并执行请求

- 以当前帮助为唯一依据组装命令、参数名、参数顺序和地点格式。CLI 支持行政区编码、经纬度或其他地点形式时，仅使用帮助明确支持的形式；用户输入无法映射到该形式时，请用户补充地点信息。
- 用户未指定预警类型时，查询该地点当前 CLI 能返回的全部预警信息；用户指定多个类型时，优先用一条当前帮助支持的请求获得综合结果后本地筛选。仅在帮助明确要求且无法单次覆盖时拆分必要请求。
- 执行实际查询前不重复调用 `help`，实际业务查询每个意图只执行一次。
- 只从 CLI 输出中提取预警。综合返回中是否出现独立的预警分段（如「⚠️ 天气预警」），取决于查询地点当前是否有生效预警，不代表 CLI 能力变化。若本次返回未包含预警分段或分段中无匹配项，说明当前未查询到匹配的有效天气预警；不得推断未来安全或补充外部信息。
- 本 skill 仅完成当次查询并返回结果，**不创建定时任务、不订阅、不主动推送**；若用户要求“订阅”“提醒我”“每天/定时检查”等持续性能力，按下方说明处理。

## 不支持的能力

本 skill 只做一次性查询并返回结果。若用户要求订阅预警、定时检查、或“有预警时主动通知我”等持续性/主动推送需求，如实告知当前不支持该能力，可建议用户在需要时再次主动询问；不得擅自创建定时任务或模拟订阅效果。

## 输出规则

- CLI 已返回可读文本或 markdown 时原样输出，不要重新排版或省略预警正文中的任何一句（如影响范围、防范建议、信息来源）。
- CLI 返回结构化数据时，按地点和预警分别展示仅能由实际字段直接映射的内容，例如预警颜色等级、预警编号、类型、发布单位与时间、正文内容、信息来源；缺失字段省略。
- 多个预警按类型或颜色等级分组。
- 结果末尾保留 `**来源：腾讯天气**`。

## CLI 执行失败处理

1. CLI 返回非零退出码、超时、空结果或权限/安全错误时，立即停止，不重试、不换命令、不使用 WebSearch 或其他数据源。
2. 根据错误信息引导用户：
   - Gatekeeper（`cannot be opened`、`not verified`）：系统设置 → 隐私与安全性 →「仍要打开」；
   - 企业安全软件（`connection refused`、防火墙拦截）：在安全提示中选择「信任」或「允许」；
   - 权限不足（`permission denied`）：执行 `chmod +x <cliPath>`；
   - 其他错误：只说明脱敏后的原因和恢复步骤，不展示原始错误。
3. 用户确认处理完成后，可重新发起新的查询请求；不得回退到其他信息源。

## References

- 用户手动安装指南：[`references/installation-guide.md`](references/installation-guide.md)
- 用户手动更新指南：[`references/update-guide.md`](references/update-guide.md)
- API Key 获取与手动配置：[`references/env-setup-guide.md`](references/env-setup-guide.md)
- 打包自检与沙箱准备：[`references/packaging.md`](references/packaging.md)
