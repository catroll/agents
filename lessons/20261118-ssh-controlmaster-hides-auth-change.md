# SSH auth tests silently reuse ControlMaster and report success

## Signal

After setting `PasswordAuthentication no`, this test still exits 0 and prints no
auth debug lines:

```bash
ssh -o BatchMode=yes -o PubkeyAuthentication=no \
    -o PreferredAuthentications=password root@host true
echo $?   # 0, no "Permission denied"
```

`ssh -vvv` also shows no `Authenticated to ...` line, which is the giveaway: no
authentication happened in this process at all.

## Cause

`~/.ssh/config` has `ControlMaster auto`, `ControlPath /tmp/ssh-root@host:22`,
`ControlPersist 86400`. The new client attaches to the already-authenticated
master connection and skips authentication, so the command succeeds regardless
of what the server now allows.

## Check

```bash
ssh -G host | grep -iE '^(controlmaster|controlpath|controlpersist)'
```

Force a genuinely new connection for both the negative and positive test:

```bash
# must fail with "Permission denied (publickey)" and exit 255
ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes \
    -o PreferredAuthentications=password -o PubkeyAuthentication=no host true

# must succeed and prove key auth works
ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes \
    -o PreferredAuthentications=publickey -o PasswordAuthentication=no host true
```

Without those two `-o` flags, "login still works" after an sshd change proves
nothing about the new policy.
