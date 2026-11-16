# 腾讯新闻 CLI 接入：较真可信源

本文件记录本 skill 依赖的 CLI 能力、已核实的调用契约与验证证据，以及仍需业务方确认的部分。

最近核实：**2026-10-28**。本次在平台 test 环境执行了 `update --force`、`version`、`help`、`help knowledge`、`help knowledge search`，并用真实问题完成可信源业务调用。

## 1. 工具与来源

| 项目 | 内容 |
| --- | --- |
| 可执行名称 | `tencent-news-cli`（Windows 为 `tencent-news-cli.exe`） |
| 用途 | 腾讯新闻的命令行查询工具；本 skill 只用其中的 `knowledge` 可信源检索能力 |
| 仓库内共享来源 | `packages/skills/src/shared/tencent-news-cli/`（脚本与共享参考文档） |
| 本 skill 调用入口 | 包内 `scripts/run-cli.sh` / `scripts/run-cli.ps1`（注入 caller，不代填业务参数） |
| 适用系统 | macOS / Linux / Windows；由共享脚本按平台选择 `.sh` / `.ps1` |
| 运行时 | 无需额外运行时；需要 API Key |

## 2. 安装、版本与下载渠道

平台开发运行使用**测试**渠道。2026-10-28 实测（强制更新后）：

```text
current_version : v1.0.18
build_date      : 2026-10-28T11:33:51
latest_version  : v1.0.18
need_update     : false
download_urls   : https://mat1.gtimg.com/qqcdn/qqnews/cli/test/...   （test 渠道）
```

| 项目 | formal（hub） | test |
| --- | --- | --- |
| CDN 根地址 | `https://mat1.gtimg.com/qqcdn/qqnews/cli/hub` | `https://mat1.gtimg.com/qqcdn/qqnews/cli/test` |
| macOS / Linux 安装脚本 | `hub/tencent-news/setup.sh` | `test/tencent-news/setup.sh` |
| Windows 安装脚本 | `hub/tencent-news/setup.ps1` | `test/tencent-news/setup.ps1` |
| SHA-256 清单 | `hub/checksums.txt` | `test/checksums.txt` |
| API Key 获取页 | `https://news.qq.com/exchange?scene=appkey` | `https://test.news.qq.com/exchange?scene=appkey&testApi=1` |
| 消耗流水 | `https://news.qq.com/exchange?scene=points` | `https://test.news.qq.com/exchange?scene=points&testApi=1` |

- **版本号相同不等于构建相同**：更新前的 `v1.0.18`（build 2026-10-21）没有 `knowledge` 命令，更新后的 `v1.0.18`（build 2026-10-28）才有。普通 `update` 只比较版本号、不会替换同版本旧构建；确认能力缺失时用 `update --force`。
- `need_update: false` 不能证明某个命令存在；能力是否具备只以当次 `help` 为准。
- 已知限制：test 安装脚本内部的默认下载根地址、校验清单与 Key 页面历史上曾指向正式环境。本次 `version` 的 `download_urls` 已指向 `/test/`。

## 3. 身份与配置

- 环境变量：`TENCENT_NEWS_APIKEY`。配置方式见包内 `references/env-setup-guide.md`，**本文件与技能包不保存任何 Key**。
- `cli-state.sh status` 的 `apiKey.status: configured` 只表示本地检测到配置，不证明远端鉴权通过。
- 2026-10-28 平台实测：`cliExists: true`，`apiKey.status: configured`，`needUpdate: false`，`cliSource: global`。

## 4. 调用契约（已核实）

`help knowledge` 原文：

> 较真可信源知识库检索，直接通过较真可信源检索智能体查询并返回结论。
> 子命令: search 检索可信源知识库内容

`help knowledge search` 原文：

> 检索较真可信源知识库内容，返回带信源引用的结论。
> Usage: tencent-news-cli knowledge search --query=<检索问题> [flags]
> Flags: --format string 输出格式: text（默认）| json；--query string 检索问题（必填）

| 项目 | 值 |
| --- | --- |
| 命令路径 | `knowledge search` |
| 必填参数 | `--query <检索问题>`；帮助建议「写清需求与返回格式」 |
| 可选参数 | `--format`，取值 `text`（默认，仅正文）或 `json` |
| 无的参数 | 没有 `--app-id`、知识库编码、相关度阈值、分页或条数参数；`knowledge` 下只有 `search` 一个子命令，没有 `list` |
| 退出码 | 成功为 0 |
| 副作用 | 只读检索，不写数据、不发消息、不发布；`--caller` 由 `run-cli` 注入，用于上报 |

最小调用（变量为任务输入，非虚构参数）：

```sh
sh scripts/run-cli.sh knowledge search --query "<用户问题>"
```

## 5. 输出契约（已核实）

- `--format text`（默认）：stdout 直接输出服务返回的正文，形如「**综合结论** … **信源验证** … 腾讯较真可信源整理，资料来源见上述引用。」。
- `--format json`：返回单个 `chat.completion.chunk` 对象，正文在 `choices[0].delta.content`，另有 `id`、`session_id`、`created`、`usage`；`finish_reason` 为 `stop`。字段以实际响应为准，解析时按路径取值，不要假设有 `choices[0].message`。
- 服务返回的正文可能**包含它自己的检索过程叙述**（例如「知识库未返回相关结果。我需要联网补查…」）以及标注「（联网补充）」的来源。这是服务输出的一部分；本 skill 按要求原样输出，不代为删改。是否需要在服务侧去掉这类叙述，属于服务端事项。
- traceid 打印在 stderr，不是业务输出，不展示给用户。

## 6. 失败处理

| 情形 | 处理 |
| --- | --- |
| CLI 未安装 | 按 `references/cli-environment.md` 安装后复查，返回 `CLI_NOT_INSTALLED` |
| 当前进程未检测到 Key | 先排除 shell/账号差异，确实缺失再引导配置，返回 `API_KEY_MISSING` |
| 401/403、无效 Key、鉴权失败 | 由用户在同一运行环境配置渠道匹配的 Key，返回 `API_KEY_UNAUTHORIZED` |
| 命令超时 | 不重试，返回 `CLI_TIMEOUT` |
| 输出为空（退出码 0） | 同一命令同一问题再调用一次；仍为空按「没有返回内容」处理，返回 `CLI_EMPTY_OUTPUT` |
| 其他非零退出或错误 | 不重试、不换命令，返回 `CLI_COMMAND_FAILED` |
| 构建缺少 `knowledge` | 先 `update --force` 复查；仍没有则返回 `CLI_CAPABILITY_MISSING` |

任何失败都**不触发 WebSearch 或其他数据源补做**。只输出脱敏后的错误类别，不回显原始错误、traceid 或 Key。

## 7. 验证证据

已执行（2026-10-28，平台 test 环境，CLI v1.0.18 build 2026-10-28T11:33:51）：

- `tencent-news-cli update --force` → 「强制重新安装当前版本 v1.0.18 … 已成功更新到 v1.0.18」；更新后 `version` 的 `build_date` 由 2026-10-21 变为 **2026-10-28**，`download_urls` 指向 `/test/`
- `help` → 命令列表新增 `knowledge 较真可信源知识库检索`
- `help knowledge` / `help knowledge search` → 如上契约
- 真实业务调用（经包内 `run-cli.sh`，注入 caller）：
  - `--query "故宫的开放预约政策是什么？"` → 退出码 0，返回正文含「综合结论」「信源验证」与来源链接
  - `--query "成人每天应摄入多少盐？" --format json` → 退出码 0，`choices[0].delta.content` 含 WHO 与中国居民膳食指南来源
- 更新前对照（2026-10-27，v1.0.18 build 2026-10-21）：`help` 无 `knowledge`，`knowledge` / `trusted` / `verified` / `source` / `rag` / `agent` 均 unknown，二进制中无相关中文命令文案 —— 这是本次「版本号相同但构建不同」的直接证据。

未验证：

- **formal 渠道**：本次只核实 test 渠道，formal 是否包含 `knowledge` 未核实。
- **Windows / macOS 平台**：本次只在 linux-amd64 上执行。
- **鉴权失败分支**：当前 Key 可用，401/403 与积分耗尽的实际返回未触发验证。
- **CLI 侧实现来源**：未获取 `knowledge` 命令的 MR/提交/发布说明，`skill.json` 的 `cli.changeRef` 目前引用 TAPD 需求链接。

## 8. 维护联络

- CLI 使用或实现问题：`quonliu`（按 wiki 协作联系人表）。
- Skill 搭建与本仓库 MR：`corinli`。
- 本 skill 负责人：`joesonqiao`。
- 测试环境 API Key 增加积分：`tatianasun`，需提供账号 `news_suid`。

以上为协作入口，不自动发送消息。
