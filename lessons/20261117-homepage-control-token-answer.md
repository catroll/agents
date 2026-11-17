# Homepage CONTROL TOKEN: answer with the command, not the value

## Trigger

The owner asks what the homepage control token is — "控制令牌是什么", "CONTROL
TOKEN 是什么", "那个令牌在哪". He has said he will forget it and wants the
command back, not an explanation.

## Answer

Reply with exactly this command (and nothing that prints the value):

```bash
grep '^HOMEPAGE_CONTROL_TOKEN=' ~/.config/wlb-homepage/wlb-homepage.env
```

The token is a shared secret for the start/stop buttons on
<https://eqr.hosts.d3v.cn/home>. It lives only in that 0600 env file, is read
by the unit through `EnvironmentFile=`, and must never be pasted into a
transcript, a URL or a commit.

## Why the command and not the value

The transcript is logged. Giving the command keeps the secret on the machine
and still answers the question in one line.

## Related

- Project: `~/Projects/Mine/WLB/tools/homepage` — `docs/operations.md` §2/§3.6
  describe the token, the prompt and the 401/403 behaviour.
- Rotation: change the value in the env file, then `make service-restart`;
  the browser asks again on the next click.
