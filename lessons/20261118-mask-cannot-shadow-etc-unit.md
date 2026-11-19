# systemctl mask fails when the unit file lives in /etc

## Signal

```text
# systemctl mask heyeAgent-install.service
Failed to mask unit: File /etc/systemd/system/heyeAgent-install.service already exists.
# systemctl is-enabled heyeAgent-install.service
disabled
```

The unit is stopped and disabled, but `is-enabled` says `disabled`, not `masked`.

## Cause

`systemctl mask` works by creating a symlink to `/dev/null` at
`/etc/systemd/system/<unit>`. When the real unit file already sits at that exact
path (installed by a vendor agent), the symlink cannot be created and mask fails.

## Check and fix

```bash
ls -l /etc/systemd/system/heyeAgent-install.service   # real file, not a symlink
systemctl is-enabled <unit>                            # disabled is already enough for boot
ls -l /etc/systemd/system/cloud-final.service.wants/   # wants symlink must be gone
```

`disable` removes the `*.wants` symlink, so the unit no longer starts at boot.
If a hard block on manual starts is required, move the unit file aside
(`mv <unit> <unit>.disabled-by-harden`) and `systemctl daemon-reload`; do not
report the item as "masked" when the command failed.
