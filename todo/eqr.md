# eqr machine health (eqr) — TODO

> Project: this host (`eqr`, Ubuntu 26.04, 16c/26G/915G NVMe)
> Prefix: E
> Next ID: E-007
> Updated: 2026-11-26

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
  - Done when: `/var/lib/rancher/k3s` (230M) and the idle system `containerd` are gone or justified
  - Ev: `du -sh /var/lib/rancher/k3s`; `systemctl is-active containerd`
