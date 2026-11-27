# eqr machine health (eqr) — TODO

> Project: this host (`eqr`, Ubuntu 26.04, 16c/26G/915G NVMe)
> Prefix: E
> Next ID: E-010
> Updated: 2026-11-27

## Theme: host maintenance

### Batch B20261125-health — fix what the 2026-11-25 health check found (done 2026-11-26)

2026-11-26 the owner decided new-api, MySQL and k3s all stay off: new-api and
MySQL are not needed, k3s is test-only. That closed the two P0s by removal
rather than repair. Context and commands:
[20261125-eqr-health-check.md](../../Projects/Mine/WLB/work/2026/Q4/11/20261125-eqr-health-check.md)

- [x] **E-001** [P0][B20261125-health][user] Decide MySQL ownership: enable host `mysql.service`, or repair the k3s mysql pod
  -> done 2026-11-26 (decision: neither runs; `mysql` stays `disabled`/`inactive`)

- [x] **E-002** [P0][B20261125-health][user] Remove the k3s mysql pod that spins at 100% of one core
  -> done 2026-11-26 (`StopUnit kubepods.slice`; gosu/traefik/redis/pause all gone, 0 container procs, load 1.74)

- [ ] **E-003** [P1][B20261125-health][user] Fix `logrotate.service` failing daily on a duplicate `cloud-init.log` entry
  - Done when: `systemctl start logrotate.service` exits 0
  - Ev: `logrotate --debug /etc/logrotate.conf | grep -i error` prints nothing

- [ ] **E-004** [P1][B20261125-health][user] Cap journald at 1G and vacuum the current 4.1G
  - Done when: `journalctl --disk-usage` is about 1G and stays there
  - Ev: `/etc/systemd/journald.conf.d/99-size.conf` exists; `journalctl --vacuum-size=1G`

- [ ] **E-005** [P2][B20261125-health][user] `apt clean` (972M) and clear the stuck Edge crash dump in `/var/crash`
  - Done when: `/var/cache/apt/archives` is near empty; `/var/crash` has no `_opt_microsoft_msedge_*`
  - Ev: `du -sh /var/cache/apt/archives`; `ls /var/crash`

### Batch B-backlog — unplanned (open)

- [x] **E-006** [P2][B-backlog] Cut swap pressure: exit WeChat when idle, or add zram
  -> done 2026-11-26 (owner added `systemd-zram-generator` with `zram-size = ram / 4`, zstd; `/dev/zram0` is swap priority 100)

- [ ] **E-007** [P3][B-backlog] Reclaim k3s leftovers if the test cluster stays unused
  - Progress 2026-11-27: `k3s-killall.sh` ran during the 80/443 outage; KUBE-/CNI- rule counts are 0
    in both `filter` and `nat`, so the port hijack cannot recur while k3s stays stopped.
    Remaining: `containerd.service` is still enabled, `/var/lib/rancher/k3s` still 230M,
    `/usr/local/bin/k3s*` binaries still installed.
  - Ev: [20261127-caddy-unreachable.md](../../Projects/Mine/WLB/work/2026/Q4/11/20261127-caddy-unreachable.md)

- [ ] **E-008** [P2][B20261127-caddy] Decide on the leftover `containerd.service` (enabled, k3s-only)
  - Done when: either disabled with a one-line reason, or documented as intentionally kept
  - Ev: `systemctl is-enabled containerd`; `systemctl status containerd --no-pager | head -5`

### Batch B20261127-caddy — caddy 80/443 unreachable (done 2026-11-27)

Root cause: k3s stopped on 11-26 without cleanup left `CNI-HOSTPORT-DNAT` / `KUBE-SERVICES`
rules hijacking host 80/443 to a dead pod. Fixed with `k3s-killall.sh`; HTTP/3 disabled so
`caddy reload` stops colliding on UDP 443. Record:
[20261127-caddy-unreachable.md](../../Projects/Mine/WLB/work/2026/Q4/11/20261127-caddy-unreachable.md)

- [x] **E-009** [P2][B20261127-caddy] Stop paying one password prompt per privileged command
  -> done 2026-11-27 (root-owned `/usr/local/bin/eqr-ops` + `/etc/sudoers.d/010-catroll-ops`;
     `sudo -n eqr-ops status caddy` works while `sudo -n true` still fails — the boundary holds;
     source `~/Projects/Mine/WLB/eqr/host/agent/`, drift check `bash eqr/host/agent/install.sh check`)
