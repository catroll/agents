# `permitlisten=127.0.0.1:15232` in authorized_keys → `Permission denied (publickey)`

Symptom: a dedicated key authenticates when its `authorized_keys` line has no
options, or only `no-pty`, but adding
`permitlisten=127.0.0.1:15232` makes every attempt fail with
`Permission denied (publickey)`. `sshd` logs `Connection closed by
authenticating user … [preauth]` and an `Invalid user`/`Disconnected` line, but
no "Invalid option" or reason for the key rejection.

Cause: the `permitlisten` value must be quoted in `authorized_keys` when it
contains `host:port`:

    restrict,port-forwarding,permitlisten="127.0.0.1:15232" ssh-ed25519 AAAA… relay

The unquoted form, and `permitlisten=15232`, both fail authentication rather
than reporting a bad option. `restrict,port-forwarding` alone is not the
problem; it works when the `permitlisten` clause is removed.

Check: install the quoted form, then test with no multiplexing and one identity:

    ssh -F /dev/null -i ~/.ssh/relay -o IdentitiesOnly=yes \
      -o BatchMode=yes -o PreferredAuthentications=publickey \
      -N -T -v -o ExitOnForwardFailure=yes \
      -R 127.0.0.1:15232:127.0.0.1:5232 relay@host

Expect `Authenticated … using "publickey"` and `remote forward success`.
A `Remote port forwarding failed` after authentication is a different problem:
the port is already held by an earlier test tunnel; find and kill that listener
on the remote host before retrying.

Negative result: `sshd -T | grep -q '^allowtcpforwarding yes'` under
`set -o pipefail` exits 141 because `grep -q` closes the pipe and `sshd` gets
SIGPIPE. A provisioning script then reports "sshd does not allow TCP
forwarding" even though the setting is fine. Capture the output first:

    settings="$(sshd -T)"
    grep -q '^allowtcpforwarding yes' <<<"$settings"

Also set `ControlMaster=no`/`ControlPath=none` for a long-lived `-N` tunnel: a
stale mux master can reuse the wrong session and print
`This account is currently not available` from a `nologin` account.
