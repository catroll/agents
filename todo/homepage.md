# WLB Homepage (homepage) — TODO

> Project: ~/Projects/Mine/WLB/tools/homepage
> Prefix: H
> Next ID: H-037
> Updated: 2026-11-20

## Theme: 本地服务统一入口

### Batch B20261118-caddy-unified-entry — 所有本机服务走 Caddy 443 子域名 (target 2026-11-18, wip)

- [x] **H-001** [P1][B20261118-caddy-unified-entry] 签发 `*.eqr.hosts.d3v.cn` 证书并扩展 Caddy 模板/安装脚本
  - Done when: 模板含 `*.eqr.hosts.d3v.cn` 块、安装脚本拷两张证书、`caddy validate` 通过
  - Ev: `~/.acme.sh/eqr.hosts.d3v.cn_ecc`（SAN `*.eqr.hosts.d3v.cn`）；`deploy/caddy/hosts.caddy.in`；`scripts/install-caddy.sh render|install`；临时实例 `127.0.0.1:18443` 验证 9 个主机 → done 2026-11-18 (见 `tools/homepage/docs/operations.md` §8.9)
- [x] **H-002** [P1][B20261118-caddy-unified-entry][user] 安装站点块与证书
  - Done when: `sudo scripts/install-caddy.sh install` 成功，`make caddy-diff` 无差异，`curl -sSI https://gold.eqr.hosts.d3v.cn/` 返回 200
  - Ev: 2026-11-18 21:50 已安装（`Caddyfile.bak.20261118215011`，证书副本 21:50，`make caddy-diff` up to date）；gold/newapi/tinyapi/cc-connect/winnie 200，ddns-go 307，markjour 302 -> done 2026-11-18
  - 首次 `sudo` 失败：`certificate not found: /root/.acme.sh/...`（sudo 把 HOME 改成 /root），已在 `b85510161` 改为从 SUDO_USER 推断
- [x] **H-003** [P1][B20261118-caddy-unified-entry][dep H-002] 把 `data/*.csv` 的端口链接换成 https 子域名
  - Done when: `make validate` 通过；导航页 10 条本地服务链接全部可打开（Cinema / Support 除外）
  - Ev: 10 条链接已改（Winnie 改链 `https://eqr.hosts.d3v.cn/`，`:5173` 是 loopback 的 Vite dev server），`make validate` 71 sites，`https://eqr.hosts.d3v.cn/home/` 200 且页面内已无 `:port` 链接；实测 8/10 可达，dsh 502（待 H-004 rebind），Cinema/Support 未启动 -> done 2026-11-18（`cccd37e44`）
- [x] **H-004** [P1][B20261118-caddy-unified-entry] 后端改绑 loopback
  - staticize admin `.env` 的 `ADMIN_HOST`、`tools/gold/app.py` 的 `host=`、tinyapi 的 `listen:` 改 `127.0.0.1` 并重启
  - dsh-web unit 改 `--host 127.0.0.1 --trusted-host dsh.eqr.hosts.d3v.cn --public-url https://dsh.eqr.hosts.d3v.cn/`（已 daemon-reload，重启见 H-006）
  - Ev: 2026-11-18 22:16 `ss -lnt` 里 8700/5000/8909 只剩回环，https 子域仍 302/200/200；提交 `7b35cc9a2` -> done 2026-11-18（dsh 的生效在 H-006）
- [ ] **H-005** [P1][B20261118-caddy-unified-entry][user][dep H-002] UFW 收口
  - 删规则 5 (`8080/tcp`)、8 (`8000/tcp`)、10 (`3080/tcp`)、11 (`8700/tcp`)、12 (`8909/tcp`)、16 (`8000/tcp v6`)
  - Done when: `sudo ufw status numbered` 里 Web 端口只剩 22 / 80 / 443（bt、3389 另计），所有子域名仍可访问
- [x] **H-006** [P1][B20261118-caddy-unified-entry][user] 最后重启 dsh-web 并改用新地址
  - Done when: 浏览器从 `https://dsh.eqr.hosts.d3v.cn/` 打开已连接（`/api/status` 不再是 403 或 502）
  - 说明: 重启会断开当前 GUI 会话（会话本身持久化）；token 见 `journalctl --user -u dsh-web.service -n 30 | grep -i token`
  - Ev: 2026-11-18 22:20:37 重启（MainPID 3896579），`ss -lnt` 里 3080 只剩 `127.0.0.1`；经 Caddy 的页面与 `/api/status` 均 401，GUI 已在 `https://dsh.eqr.hosts.d3v.cn/` -> done 2026-11-18
- [ ] **H-008** [P3][B-backlog] 升级 Caddy 2.6.2（2022 年）到当前稳定版
  - Done when: 升级后 `/etc/caddy/Caddyfile` 不报弃用项，本次子域名入口与 /home 全部回归
- [ ] **H-009** [P3][B-backlog] 决定 Cinema / SendCloud Support / NewAPI Admin 去留
  - 三者入口都是 502：Cinema、Support `autostart=false`；NewAPI Admin 的 `newapi-web.service` 自 2026-11-18 20:06 起 inactive（测试实例，已按要求停用）。要么启动并保留，要么从 CSV 删除
  - Done when: 导航页不再存在「点了必定 502」的条目
- [x] **H-010** [P1][B20261118-caddy-unified-entry][user] 启用每日证书同步 timer（需要 root）
  - 背景：Caddy 不会监视证书文件，而 Caddyfile 指向 `/etc/caddy/certs` 的副本；原来续期后要手工重跑 install。现已加入 `scripts/sync-caddy-certs.sh` + `wlb-caddy-certs.{service,timer}`（每日 21:45，acme.sh 21:10 之后）
  - Done when: `sudo scripts/install-caddy.sh install` 装上并启用 timer；`systemctl list-timers wlb-caddy-certs.timer` 显示下次 21:45；`journalctl -u wlb-caddy-certs` 首次同步应为 `installed: d3v.cn` + 另外两份 `up to date`
  - Ev: `make caddy-cert-check`（当前输出 hosts/eqr `up to date`、**d3v.cn `would install`**：装的是 8/10 副本，2026-11-04 已过期，而 acme.sh 已续到 2027-02-15；`install` 会一并修复）；`sudo scripts/sync-caddy-certs.sh --dry-run` 手动比较
  - 2026-11-18 22:03 首次 `sudo install` 失败：`CERT_SRC3: 未绑定的变量`（第三份证书的源目录只在这条 root 路径上使用，`bash -n` 与非 root dry-run 都覆盖不到）；已在 `a59d1edb1` 补默认值，并新增 `scripts/tests/test-install-caddy.sh` + `make scripts-test` 用桩跑两个 root-only 助手函数，重跑即可
  - Ev: 2026-11-18 22:07 重跑成功；`wlb-caddy-certs.timer` active (waiting)，下次 `2026-11-19 21:46`；`make caddy-cert-check` 三份证书全部 `up to date`（d3v.cn 过期副本已修复）-> done 2026-11-18

- [ ] **H-011** [P2][B20261118-caddy-unified-entry] 验证证书同步 timer 首次运行
  - 2026-11-19 21:46 首跑；确认 `wlb-caddy-certs.service` 成功、Caddy 仍服务当前证书
  - Done when: `systemctl status wlb-caddy-certs.service` success 且 `make caddy-cert-check` up to date

### Batch B20261118-auth-service — 独立认证服务与账号迁移 (target TBD, open)

- [x] **H-012** [P1][B20261118-auth-service] 引入独立认证服务 tinyauth，并把在用账号并入
  - 2026-11-18 收尾：4 个 tinyauth 用户（catroll/admin/betty/woody），三个应用本地登录关闭、`Remote-User` 身份 200，门禁矩阵与回滚演练见 `docs/auth.md` §6.4 -> done 2026-11-18
  - 2026-11-18 首次 `sudo scripts/migrate-auth-users.sh apply` 因 sudo 把 HOME 置为 /root，三个源路径都被判为缺失，脚本静默 no-op（users 仍只有 catroll）；已改为从 SUDO_USER 解析家目录、源为空时 die，测试改走默认 CALLER_HOME 布局（`db0518e97`），待重跑
  - 决策 2026-11-18：用户同意「独立服务」方案；先做门禁，之后必须做一次迁移，保证所有在用账号合并到新服务
  - 服务：tinyauth（单二进制/容器，SQLite，bcrypt+TOTP，Caddy `forward_auth`），锁版本；若单人维护的版本迭代造成负担，退回 Authelia
  - 一期（门禁，不改账号）：全量备份 → gold 试点 → 铺到 `*.eqr.hosts.d3v.cn`（含 `/home`）；排除机器接口（tinyapi `/v1/*`、ddns-go 回调、dsh `/api` 如需要）
  - 二期（迁移）：TinyAPI 的 bcrypt 可复用；Winnie / Support / staticize / DDNS-GO 重置密码后导入；支持 OIDC 的应用直连，其余应用用 `Remote-User` 头（需改应用），之后停用应用自带登录
  - 回滚：删 `forward_auth` + reload；旧账号库保留 30 天
  - Done when: 一期所有子域需登录且机器接口正常；二期新服务是唯一账号源，旧应用登录停用且备份可还原

- [x] **H-013** [P0][B20261118-auth-service] 认证设计文档与备份脚本
  - `docs/auth.md`（架构/迁移矩阵/回滚/安全成本）+ `scripts/backup-auth-state.sh`（SQLite backup API、env、users.yaml、ddns-go 配置）
  - Done when: 文档提交；脚本跑一次产出目录含 manifest 与 sha256，且可重复执行
  - Ev: 2026-11-18 `6697bf9c9`；备份 `~/.cache/auth-backup/20261118-225144/`（5 个文件 + MANIFEST.sha256）；ddns-go 配置需 sudo 补拷 -> done 2026-11-18
- [x] **H-014** [P0][B20261118-auth-service] 部署 tinyauth 系统服务（锁 v5.2.0 + sha256）
  - 2026-11-18 文件与临时验证已完成（`6697bf9c9`）：登录写 eqr.hosts.d3v.cn 域 cookie、forward_auth 200 带 Remote-User、浏览器 UA 302、登出正常
  - 2026-11-18 23:20 首次 sudo 安装：创建管理员时解析失败（TTY 输出 CRLF/颜色），tinyauth 未起来；但随后的 `install-caddy.sh install` 已写入门禁 → 所有受保护服务 502。已用临时实例顶住（管理员 catroll，密码在 `~/.cache/auth-backup/tinyauth-temp/password.txt`），并修复：创建用户输出容错、`install-caddy.sh` 安装前健康检查、`install-tinyauth.sh` 拒绝非 systemd 实例占用 3000 且等待前先确认 unit active
  - 2026-11-18 23:25 第二次失败：用户其实创建成功（users.txt 1 行），但 `port_owned_by_other` 在“端口空闲”的正常结果上 `return 1`，`set -e` 直接退出，unit 未安装。已改为正常返回 0、冲突才 die；新增 `scripts/tests/test-install-tinyauth.sh` 用临时目录 + 桩 systemctl/curl 走完安装路径与 Caddy 预检，`make scripts-test` 两项全过（退出 0）
  - 2026-11-18 23:39 系统服务安装成功：unit enabled+active、health 200、users 1、`make caddy-diff` up to date；`/home` 与所有服务均为 302 门禁，DSH 401、TinyAPI `/v1` 应用 401 -> done 2026-11-18
  - 2026-11-18 23:30 另外修掉 `caddy-diff` 的假漂移：winnie installer 把块追加在我们后面，整文件 diff 会把顺序变化当漂移；改为只比较自己的标记块并拒绝重复标记，测试覆盖「后面追加别人的块=干净」「块内改动=漂移」。`make scripts-test` 两项均 exit 0（`341734cc3`）
  - `deploy/tinyauth/{tinyauth.env.example,tinyauth.service.in}` + `scripts/install-tinyauth.sh install|uninstall|check`
  - 配置 127.0.0.1:3000、APPURL=https://auth.eqr.hosts.d3v.cn、users.txt、SQLite、analytics/resources 关闭
  - Done when: `systemctl status tinyauth` active；`curl 127.0.0.1:3000/api/health`（或等价）200
- [x] **H-015** [P0][B20261118-auth-service] Caddy forward_auth 接入（gold 试点→全量）
  - 2026-11-18 模板完成并已实装（`77e7b9341`、`cb0565f`）；线上验证：8 个服务 + `/home` 302，DSH 401，`/v1` 应用 401 -> done 2026-11-18
  - 模板加 `(wlb_auth)` snippet、门户 `auth.eqr.hosts.d3v.cn` 站点块、各服务 `handle` 内 `import wlb_auth`
  - 排除 DSH 整站与 TinyAPI `/v1/*`；先运行时 reload 验证 gold 302→登录→200→`Remote-User`
  - Done when: gold 未登录 302、登录后 200 且上游收到 Remote-User；全量后其余服务同样；用户执行持久化 install
- [x] **H-016** [P0][B20261118-auth-service] 迁移 TinyAPI（bcrypt 复用 + Remote-User）
  - 2026-11-18 apply 后 admin/betty/woody 已导入 tinyauth，tinyapi `local_login: false`、`/login` 403、`/console` 经 Remote-User 200 -> done 2026-11-18
  - 2026-11-18 代码完成（`f7addbb30`）：`system.proxy_auth.trust` + `local_login`，Remote-User 仅回环可信，转成 Console session；测试覆盖信任边界；`go test ./...` 通过。启用待门禁上线
  - 启用：`config/config.yaml` 已加 `system.proxy_auth.trust: true`，重新 build 二进制后重启，实测 `woody` 200 / 未知用户 303；待浏览器验证后 `local_login: false`（注意 unit 指向构建产物，重启前必须 rebuild）
  - `users.yaml` 的 bcrypt 原样写入 tinyauth users.txt；TinyAPI 控制台信任来自 Caddy 的 Remote-User，停用本地密码登录
  - Done when: 用原密码经 tinyauth 登录；控制台免二次登录；`/v1/*` 仍按 API key 工作
- [x] **H-017** [P0][B20261118-auth-service] 迁移 staticize admin
  - 2026-11-18 staticize 不导入账号（无账号库），`ADMIN_LOCAL_LOGIN=0`、`/login` 403、`Remote-User: admin` 200；回滚开关实测 200↔403 -> done 2026-11-18
  - 2026-11-18 代码完成（`e2d08eaf2`）：`ADMIN_TRUST_PROXY_AUTH` / `ADMIN_LOCAL_LOGIN`，6 个测试通过；全量 247 项测试仅 1 个与本次无关的既有失败（test_header_logo CSS 宽度）。启用待门禁上线
  - 2026-11-18 结论：staticize 没有独立账号库（env 只是密码），已从迁移脚本移除；`ADMIN_TRUST_PROXY_AUTH=1` 已开，实测 `Remote-User: admin` 直达 200；待 tinyauth 的 admin 导入后设 `ADMIN_LOCAL_LOGIN=0`
  - tinyauth 建同名用户（重置密码）；admin 加 `AUTH_TRUST_PROXY`（仅接受 loopback 的 Remote-User），停用 env 登录
  - Done when: 经 tinyauth 登录后直接进后台；停用后 env 密码无法登录
- [x] **H-018** [P1][B20261118-auth-service] 迁移 SendCloud Support
  - 2026-11-18 复核确认登录委托上游 Nexus，本地 users 表不在登录路径；作为例外记录（只受边缘门禁保护），不并入 tinyauth -> done 2026-11-18
  - 2026-11-18 复核：登录实际委托上游 Nexus helpdesk，本地 `tickets.db` 的 users 表不在登录路径上 → 账号无法并入 tinyauth，改为例外（只加边缘门禁，应用内 Nexus 登录保留），需在文档与验收里明确
  - Done when: 两个账号都能经 tinyauth 进入；旧登录失效；数据（工单）不变
- [x] **H-019** [P0][B20261118-auth-service] 迁移 Winnie 控制台
  - 2026-11-19 复核 `[x]` 不成立：tinyauth 登录后控制台仍停在本地登录页。两处根因：`/api` 不过门禁 → 前端无 token 探测 `/auth/me` 拿不到 `Remote-User` 而 401；且 Caddy 未删客户端 `Remote-*`，实测伪造 `Remote-User: admin` 经 `/api/v1/auth/me` 直达 200（冒充漏洞）。已改：Caddy 模板对 `/api`、`/api/*` 加门禁、机器凭据旁路、所有去上游路由先删 `Remote-*`；API 新增 `auth.proxy_user_map`（本机 `catroll→admin`）；控制台先探测边缘身份再回退 token。本地 8443 + 真实 dist + 假 tinyauth 的 Firefox 实测 `Dashboard` 无登录页，单测 5+11 通过。详见 `docs/auth.md` §6.6。2026-11-19 01:00 热加载候选配置；用户 01:03 已跑 installer 落盘（`scripts/install-caddy-winnie.sh --check` 报 in sync）。01:09 又修掉第二层：uvicorn 默认 proxy headers 把 `request.client` 改写成 `X-Forwarded-For`（浏览器公网地址），回环判断因此仍然拒绝 Caddy 的 `Remote-User`；`serve-api.py` 关 `proxy_headers`，新增 `winnie_api.proxy.TransportAwareProxyHeaders` 先把传输层 peer 记进 `context`，信任判断读它。修复后直连 API 带公网 XFF + `Remote-User` 由 401 变 200；本地 8443 + 真实 dist + 非回环 XFF 的 Firefox 实测进 `Dashboard`、`/api/v1/meetings` 200。2026-11-19 01:23 用户在浏览器刷新后直接进了控制台；API 日志同一时刻 `2409:… - "GET /api/v1/auth/me" 200`，Caddy 上游 4 次 200 -> done 2026-11-19
  - 2026-11-18 Winnie 用户 cleanup→admin（50 条按 users.id 跟随，备份 20261118-235030），`auth.local_login: false`、登录 403、`Remote-User: admin` 经 `/auth/me` 200 -> done 2026-11-18
  - 2026-11-18 代码完成（`9161659`）：`auth.trust_proxy` / `auth.local_login`，API 仅信任回环 Remote-User；控制台无 token 探测 `/auth/me`、跳过登录页、隐藏改密、登出去门户；4 个新测试 + 15 个 auth 测试通过，console 构建成功
  - 2026-11-18：把 `cleanup` 改名为 `admin`（`winnie/scripts/rename-user.py`，50 条引用按 users.id 跟随，备份 `~/.cache/auth-backup/20261118-235030/winnie-pre-rename.db`），实测 `Remote-User: admin` 经 `/auth/me` 200；`auth.trust_proxy` 已开，待 tinyauth admin 导入后 `auth.local_login: false`
  - Done when: 经 tinyauth 打开控制台无需再登录；旧密码失效；手机端可用
- [x] **H-020** [P1][B20261118-auth-service] 例外与收尾
  - 2026-11-18 例外（DSH token / DDNS-GO 第三方 / Support Nexus）与旧凭据 30 天保留策略写入 `docs/auth.md` §6.4；TOTP 未启用（可选） -> done 2026-11-18
  - DSH（token）与 DDNS-GO（第三方登录）的例外写进文档；旧账号库保留 30 天与清理脚本；TOTP 开启说明
  - Done when: `docs/auth.md` 例外与清理命令齐全，`make auth-check` 通过
- [x] **H-021** [P1][B20261118-auth-service] 回滚演练与全量验证
  - 2026-11-18 回滚演练实测：staticize/tinyapi 本地登录 200→403，Winnie 401→403；门禁矩阵 8 服务+/home 302、DSH 401、/v1 401；记录见 `docs/auth.md` §6.4（`2bc09db6d`） -> done 2026-11-18
  - 逐应用关掉门禁/恢复旧登录、验证回滚；全量 10 个子域 + `/home` 实测记录
  - Done when: 回滚步骤实测成功并写回文档；§8.10 有完整验证表
- [ ] **H-031** [P2][B20261118-auth-service] 评估/落实 homepage admin 与启停接口的门禁与 token 退场
  - 现状：`/home` 公开；`/home/admin`、`/home/api/admin/*`、`/home/api/services/action` 只校验 `HOMEPAGE_CONTROL_TOKEN`，Caddy 未拦
  - 方案 A：给上述路径加 `forward_auth`（token 保留为纵深防御）；方案 B：再加应用侧 `Remote-User` 信任，token 变可选/可退场（需 Go + JS + 两个 Caddy 模板 + installer）
  - 2026-11-19 用户决定：彻底去掉 token（方案 B）。已完成应用侧与模板：token 从 config/env/校验/handler/两个前端全部移除；写入口改为只信任 loopback `+ Remote-User`，无头 403/401（fail closed）；Caddy 两个站点块对 `/home/admin`、`/home/api/admin/*`、`/home/api/services/action` 加 `forward_auth`；`go test ./...` 与 `make scripts-test` 通过（`e64ff3ab7`、`9536a75`）。已实测直连应用：无头 403/401、带头 200。**待用户跑两个 installer 后**验证 `/home` 200、`/home/admin` 未登录 302、登录后 200
  - Done when: 路径门禁生效；按选定方案 token 的保留/退场写入 `docs/auth.md`，`make scripts-test` 与 `go test ./...` 通过

- [ ] **H-032** [P1][B20261118-auth-service][user] ddns-go / cinema 接入面收口（回环 + ddns-go fork 消费 tinyauth 身份）
  - cinema 的 `server.addr` 从 `":8701"` 改为 `"127.0.0.1:8701"`（live 与 eqr 备份一致）；ddns-go 改用本地 fork `v6.17.9-wlb.1`（`~/Projects/Forked/ddns-go`，分支 `wlb-tinyauth`，补丁副本 `eqr/services/ddns-go/patches/`），unit 改为 `/opt/ddns-go/ddns-go -l 127.0.0.1:9876 -trustProxyAuth -proxyLogoutURL https://auth.eqr.hosts.d3v.cn/logout`
  - `-trustProxyAuth` 仅在「flag 打开 + 回环对端 + 非空 `Remote-User`」时跳过本地登录，其余回落 307（fail closed）；以 `{` 开头的未展开 placeholder 也按无身份拒绝；Caddy `@ddnsgo` 在 `route` 里先 `request_header -Remote-*` 再 `forward_auth`，防止伪造头
  - 待用户（root，2026-11-19 修退出后重装）：`cd ~/Projects/Forked/ddns-go && sudo scripts/install.sh` → `cd ~/Projects/Mine/WLB/eqr/restore && ./restore.sh --apply --only ddns-go` → `sudo systemctl restart ddns-go`（Caddy 已装，无需再跑）
  - Done when: `/opt/ddns-go/ddns-go -v`=v6.17.9-wlb.1；`curl 127.0.0.1:9876/` 无头 307、带头 `Remote-User` 200；经 Caddy 登录后 ddns-go 不再出现自己的登录页；点退出后到门户登录页（`/logout` 302 到门户 `/logout`）；`ss` 只剩回环
  - Ev: 2026-11-19 fork `go test ./web` 通过（4 个测试 16 个子用例）、`go vet ./...` 通过；二进制本机实测 307/200/307/307；临时 Caddy + 桩 auth 全链路实测「伪造头且 auth 不回头 307 / auth 回 alice 200 / 直连 placeholder 307」；Caddy 渲染后 `caddy validate`（去掉 tls 行）Valid；`make scripts-test` 通过；`restore.sh --apply --only ddns-go --dry-run` 只写该 unit；退出修复另证 `web/logout_test.go` + 临时 Caddy 全链路 302/Location/清 cookie -> 待用户重装二进制/unit 后 done

- [ ] **H-033** [P3][B-backlog] ddns-go fork 跟随上游发布（重放补丁并重建）
  - 基线上游 `v6.17.9`；新 tag 出来后 `git fetch upstream --tags`、新分支、cherry-pick 三个补丁提交、`make test`、`make build VERSION=<tag>-wlb.1`、`sudo scripts/install.sh`
  - Done when: 新版本装到 `/opt/ddns-go` 并验证无头 307 / 带头 200；`WLB-PATCH.md` 与 `eqr/.../patches/` 同步更新

### Batch B20261118-search-admin — 主页搜索框与管理界面 (target 2026-11-18, wip)

- [x] **H-022** [P1][B20261118-search-admin] 主页网络搜索框：五个引擎 + 默认引擎配置
  - 百度 / 谷歌 / Bing / GitHub / Wikipedia；`search.default_engine` 配置；页面记忆上次选择（localStorage）
  - Done when: 页面渲染搜索框与引擎切换，提交后跳到对应引擎结果页；无 JS 时默认引擎仍可用；`make check` 通过
  - Ev: `94fedc7a9`；`make check` 通过；Firefox BiDi 实测切换 GitHub→`type=repositories`、reload 保持选择、百度→`wd`、420px 无横向溢出 -> done 2026-11-18
- [x] **H-023** [P1][B20261118-search-admin] 管理端数据层：设置持久化 + CSV 安全写入
  - 默认引擎存 `.cache/settings.json`（原子写）；分组/站点按 CSV 行编辑，保留注释行与顺序，原子替换；改名保留数字前缀；拒绝删最后一个分组
  - Done when: 单元测试覆盖增删改、改名、注释保留、坏 URL 拒绝、临时文件清理
  - Ev: `f96a47c2e`；`make check` 通过；单测覆盖注释保留、改名保留前缀、拒绝删最后分组/路径穿越/坏 URL、原子写无临时文件 -> done 2026-11-18
- [x] **H-024** [P1][B20261118-search-admin] 管理 API：令牌 + 同源 + 限速
  - `GET /api/admin/state`、`PUT /api/admin/settings`、`POST/PUT/DELETE /api/admin/groups`；复用 `HOMEPAGE_CONTROL_TOKEN`；失败尝试限速；路径穿越与请求体上限
  - Done when: 无令牌 401、跨站 403、禁用时 fail closed；CRUD 实测通过；有安全与成本评审
  - Ev: `df16a11e2`；curl 实测 401/403/200、设置改名组删除、首页即时用新默认引擎；`go test` 覆盖写限速与 415 -> done 2026-11-18
- [x] **H-025** [P1][B20261118-search-admin] 管理界面页面
  - `/admin`：解锁、默认引擎、分组增删改名、URL 行增删改与上下移、保存；键盘可达，移动端可用
  - Done when: 浏览器实测完成一次「新增分组 → 加站点 → 改默认引擎 → 刷新首页生效」
  - Ev: `06b01c57e`；Firefox BiDi 实测解锁→改 Bing→新增「UI测试」分组→加站点→保存→刷新后仍在，首页 Tab 与默认引擎同时生效；420px 无横向溢出 -> done 2026-11-18
- [x] **H-026** [P2][B20261118-search-admin] 文档、部署与回归
  - 更新 `config.example.yaml`、`docs/operations.md`（配置/CSV 写回/安全成本/设计决策/验证）、service unit 写权限、README 特性表
  - Done when: `make check`、本地实例端到端与首页/管理页回归记录写入 §8.10；提交完成
  - Ev: `a1b54840f`；`make check`、`make validate`（6 组 71 站）、`make scripts-test` 通过；§2.1/§2.2/§6/§7/§8.10 已写；`make service-diff` 只有预期的 `ReadWritePaths` 差异，线上未部署/未重启 -> done 2026-11-18
- [x] **H-027** [P1][B20261118-search-admin] 部署管理界面到线上并验证
  - 备份 `config.yaml` → 启用 admin → `make service-install` 重装 unit（`ReadWritePaths` 含 `data/`）→ 重启
  - Done when: `/home/admin` 200、无令牌 401、默认引擎与 CSV 写入实测成功、公开入口 200、测试分组已清理
  - Ev: 2026-11-18 23:16 上线（MainPID 4019412）；`make service-diff` up to date；loopback/public `/home/admin` 均 200；无令牌 401；设置写 200、建组/加行/删组全成功且 `data/` 回到 6 个 CSV；回滚备份 `.cache/deploy/config.yaml.20261118231644.bak`；文档 `a32976c48` -> done 2026-11-18
- [x] **H-028** [P2][B20261118-search-admin] 搜索引擎移到页头，筛选框移到 Tab 行右侧
  - 去掉 hero；页头品牌右侧放引擎切换 + 搜索框；筛选框 220×34 放 Tab 行最右端并垂直居中；窄屏自适应
  - Done when: 1280/1024/800/420 无横向溢出，页头/行高协调，搜索与筛选功能不变，已部署
  - Ev: `4d1316d55`；BiDi 实测 1280 页头 75px、筛选 220×34 中心差 0.5px；1024 同行；800 页头换行；420 无溢出且筛选占满下行；GitHub 切换仍到 `type=repositories`；`make service-install` 23:27 重启（PID 4067109），`service-diff` up to date；文档 `f81cc0de8` -> done 2026-11-18
- [x] **H-029** [P2][B20261118-search-admin] 搜索框居中、图标引擎下拉、设置按钮、注释页脚
  - 搜索引擎改为搜索框内、按钮左侧的图标下拉；页头三段式（品牌/居中搜索/右侧齿轮）；页脚模板注释保留
  - Done when: 1280/1101/1100/1024/420 无溢出且搜索居中，图标下拉可选可键盘操作，齿轮进管理页，页脚不渲染，已部署
  - Ev: `51d1edc5d` + `4e3ee2f40` + `c9e6fad36`；BiDi 1280 搜索 640×42 中心 640、齿轮 38×38 右缘 1264；1101 单行；1100/1024 换行仍居中；420 无溢出；选 Wikipedia/GitHub 动作与参数正确，重载保持；`service-install` 23:38 重启（PID 4104027），`service-diff` up to date；公开入口仍被并行 tinyauth 门禁 401 -> done 2026-11-18
- [x] **H-030** [P1][B20261118-search-admin] 修复图标下拉改写吞掉 Tab/筛选脚本
  - 从 `4d1316d55` 恢复 Tab/筛选 IIFE；加 `TestHomepageScriptInitialisesTabs` 守卫；重新部署并实测
  - Done when: 线上 `tabs-on` 生效、6 个 Tab 与筛选框可见、切 Tab/过滤/`/` 聚焦正常
  - Ev: `db32527bf`；`service-install` 2026-11-19 00:06 重启（PID 4170027），`service-diff` up to date；BiDi 实测 tabbar flex、filter block、切 Tab 与 `deepseek` 过滤正常；文档 `5712c5423`，lesson `docs/lessons/20261119-js-splice-swallows-neighbor-block.md` -> done 2026-11-19

### Batch B20261119-page-identity — 页头身份与按钮门控 (target 2026-11-19, wip)

- [ ] **H-034** [P1][B20261119-page-identity][user] 页头用户名菜单、登录入口与服务操作按钮的登录门控
  - 未登录显示齿轮作为登录入口（`admin.enabled` 时指向 `/home/admin`；不显示用户名菜单与操作按钮）；登录后右上角显示用户名，下拉为「设置」+「退出」（退出目标来自 `page.logout_url`，线上指门户 `/logout`）。Caddy 对 `/home/` 做可选 `forward_auth`（有会话注入 `Remote-User`，无会话匿名放行），受保护路径的 401 由 `handle_response` 转 302 到 tinyauth 登录页；tinyauth 不可达时公开页回退匿名、受保护路径仍 fail-closed
  - 两个模板都要改：`tools/homepage/deploy/caddy/hosts.caddy.in` 与线上生效的 `~/Projects/Mine/winnie/deploy/caddy/winnie-console.caddy`（精确主机遮蔽通配块）
  - Done when: 线上登录后 `/home/` 显示用户名、下拉含「设置」「退出」与按钮；未登录显示齿轮但无菜单/按钮，点齿轮经门户登录后回到 `/home/admin`；action 仍 401；tinyauth 宕机时 `/home/` 仍 200 匿名
  - Ev: 2026-11-19 代码与模板完成；`make check`、`make validate`、`make scripts-test` 通过；临时 Caddy + 真实 tinyauth / 桩 auth 全链路（匿名/有会话/伪造头/auth 宕机/401→302 到门户）与 Firefox BiDi 实测通过，记录在 `docs/auth.md` §6.7、`docs/operations.md` §8.14、§8.16。2026-11-19 02:25 应用已重启（`make service-install`，版本 `42c4d6181`，MainPID `213483`，直连匿名只有齿轮、带 `Remote-User: catroll` 有菜单/「设置」/「退出」/13 按钮）；Caddy 两份配置仍待用户跑 `sudo scripts/install-caddy-winnie.sh` 与 `sudo scripts/install-caddy.sh install`（`--check`/`caddy-diff` 均报预期 drift），落盘后在浏览器验证齿轮→登录、登录后右上角用户名与「退出」

### Batch B20261120-links — 常用链接补充 (target 2026-11-20, done)

- [x] **H-035** [P2][B20261120-links] 补充个人工具、邮箱账号与邮件投递工具链接
  - 个人 Tab：工具列加 Todoist / docsmall / 佐糖，开发/社区列加 Gitee / ECharts，新增「邮箱」列（Gmail / 网易 / Outlook / iCloud / Proton）
  - 工作 Tab：新增「邮件」列（MxToolbox 邮件头与 SuperTool、Outlook SNDS、Cisco Talos、Email Checker、Googlebot 验证、Google/Yahoo 发件人规范）
  - 伦敦金（wzg.com/gold/）已在理财 Tab，未重复添加；MxToolbox 邮件头两条 URL 为同一工具，取 `EmailHeaders.aspx` 一条
  - Done when: `make validate` 通过；线上 `/home/` 渲染出两列新链接
  - Ev: 2026-11-20 `make validate` → 6 groups / 92 sites；`make check` 通过；`curl /home/` 200，18 条新 URL 均在 href 中，个人 Tab 出现「邮箱」列、工作 Tab 出现「邮件」列

- [x] **H-036** [P2][B20261120-links] 按用途重整个人 Tab 的分组
  - 「eqr」→「项目」；「本地」→「服务」；Winnie、Cinema 归入「项目」，DeepSeek Harness 归入「服务」；「开发/社区」→「开发者」并删除 知乎（阅读 Tab 已有）
  - Done when: `make validate` 通过；线上 个人 Tab 列为 项目/服务/Woody/AI/搜索/工具/云服务/影音/开发者/邮箱，个人 Tab 不再含 知乎
  - Ev: 2026-11-20 `make validate` → 6 groups / 92 sites；`make check` 通过；`curl /home/` 200，项目列 6 项（Markjour/NewAPI/TinyAPI/TOTP/Winnie/Cinema）、服务列 4 项（DeepSeek/CC-Connect/DDNS-GO/Support）、开发者列 5 项，个人 Tab `知乎` 出现 0 次，阅读 Tab 保留 3 条 知乎 链接

