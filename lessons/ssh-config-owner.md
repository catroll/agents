# `ssh` fails on every host: pass `-F ~/.ssh/config`

**Signal.** Every `ssh` invocation dies immediately with exit 255, before opening
a connection, and the message names a *system* file, not your host or key:

```
Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
```

A valid `~/.ssh/config` entry and a working key change nothing — even a host you
reached five minutes ago now fails.

**Cause.** `/etc/ssh/ssh_config` line 19 is `Include /etc/ssh/ssh_config.d/*.conf`.
On this workstation that directory is owned `nobody:nogroup` mode `777` and holds
a symlink into `/usr/lib/systemd/ssh_config.d/`. ssh refuses a config file it
cannot attribute to root or the current user, and one bad include kills the whole
run. Check with:

```bash
stat -c '%n owner=%U group=%G mode=%a' /etc/ssh/ssh_config.d/*
```

**Fix.** Give `-F` explicitly. Per `man ssh_config`, a command-line `-F` makes ssh
ignore the system-wide file as well as the default per-user one:

```bash
ssh -F ~/.ssh/config -o BatchMode=yes <host> 'command'
```

Do not try to `chown`/`chmod` the system path: it is outside the workspace, the
sandbox denies it, and it is not yours to fix.

**Generalisable bit.** When ssh's error names a config file, the failure is
client-side and host-independent — reach for `-F ~/.ssh/config` before suspecting
the server, the key, or the network. Wrapping it as `SSH="ssh -F ~/.ssh/config"`
saves rediscovering this on every call.

