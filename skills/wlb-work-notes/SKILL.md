---
name: wlb-work-notes
description: >-
  WLB 仓库 work/<年>/Q<季>/<月>/ 下工作笔记与报告的命名、存放和更新规则。当要在 work 目录下
  新建排查记录、问题反馈、报告、附件，或要给某个已有笔记起名/找位置时使用。规定
  `YYYYMMDD-<主题>.md` 形式、域名写法、-report 后缀、周期文件与原始输出的命名。
---

# WLB 工作笔记命名规则

WLB 仓库（= 含 `.git` 的仓库根，通常 `~/Projects/Mine/WLB`）里，所有工作记录都放在 `work/` 下，**文件名本身就是索引**，所以命名必须能直接看出「哪天、什么事」。

## 存放位置

```
WLB/work/<年>/Q<季度>/<月两位>/
```

- 例：`work/2026/Q4/10/` 是 2026 年 10 月（Q4）。
- 注意季度与月份对应：`Q3/09`、`Q4/10`。
- 仓库根有软链接：`S_CURRENT` → 当前周期目录、`S_LAST` → 上一周期、`S_NEXT` → 下一周期。写文件时用真实路径 `work/2026/Q4/10/`，不要写进软链接目录里。
- 一个持续多天的项目可以自建**同名目录**，例如 `work/2026/Q3/09/20260921-newapi/`，里面的笔记仍按同样规则命名。

## 主规则：`YYYYMMDD-<主题>.md`

```
20261009-hub-shanedit-com-logs-missing.md
└─日期─┘ └────────主题────────────┘
```

| 部分 | 规则 |
| --- | --- |
| 日期 | `YYYYMMDD`，**事情发生/处理当天**，不一定是写文件的当天 |
| 分隔 | 日期与主题之间一个 `-` |
| 主题 | 全小写 kebab-case，英文；能一眼看出对象和事由 |
| 扩展名 | `.md` |

### 主题里写域名 / 主机

域名的点号换成连字符，**保留 `com`**：

- `hub.shanedit.com` → `hub-shanedit-com`
- `token.shanedit.com` → `token-shanedit-com`
- 例：`20261008-hub-shanedit-com-network-problem.md`

### 主题里写项目 / 产品

直接用项目名，可带事由：`20260921-newapi-deploy.md`、`20260924-newapi-models.md`。

## 同名同日 = 同一个文件，继续改

**同一天、同一主题再次出现时，更新原文件，不要新建 `-2`、`-v2`、`-final`。** `work/` 下的文件是活文档，git 历史负责记录改动过程（仓库里 `20261008-hub-shanedit-com-network-problem-report.md` 就被连续提交了多次）。

新建前先 `ls` 一下目标目录，确认没有同主题的旧文件。

## 后缀约定

| 后缀 | 含义 | 例 |
| --- | --- | --- |
| 无 | 工作笔记 / 排查过程 | `20261008-hub-shanedit-com-network-problem.md` |
| `-report` | 正式对外报告（与同名工作笔记配对） | `20261008-hub-shanedit-com-network-problem-report.md` |
| `-weekly` | 周报 | `202610-12-18-weekly.md` |

## 其他两类文件

**周期文件**（周计划/周报）用日期区间，不是单日：

```
202610-12-18.md           # 10-12 ~ 10-18 这周
202610-12-18-weekly.md    # 同一周的周报
```

**原始输出 / 附件**用 `.txt`，同日同主题加限定词区分：

```
20261009-hub-shanedit-com-latency-morning.txt
20261008-hub-shanedit-com-latency-peak.txt
```

诊断脚本、nginx 配置快照等整目录产物，用 `<同名前缀>-<类别>/` 建目录收纳，例如 `20261008-hub-shanedit-com-nginxconf/`。

## 目录内的固定文件

`README.md`、`TODO.md`、`REVIEW.md`、`_weekly.md` 是周期目录的固定文件，**不套用上面的日期规则**。

## 检查清单

新建文件前过一遍：

1. 目录是不是 `work/<年>/Q<季>/<月>/`？
2. 日期是事情发生那天吗？
3. 主题是不是全小写 kebab-case、域名点号已换成连字符？
4. 同目录有没有同日同主题的旧文件？有就改那个。
5. 是正式报告就加 `-report`；是原始输出就用 `.txt`。
