# Reading `/proc/<pid>/cmdline` makes the capture look like a binary file

## Signal

```text
$ file audit/probe2.txt
audit/probe2.txt: data
$ read audit/probe2.txt
Error: cannot read "...": binary file / invalid UTF-8 text
```

`grep -c $'\x00' audit/probe2.txt` reports thousands of hits, yet the script
itself completed (`exit=0`) and most sections are normal text.

## Cause

`/proc/<pid>/cmdline` separates argv with NUL (`0x00`). A collection script that
does `cat /proc/$pid/cmdline` or `tr '\0' ' ' < /proc/$pid/cmdline` and then
redirects the whole script output keeps those NULs. `file` classifies the whole
capture as `data`, and UTF-8 readers refuse it.

## Check and fix

Strip NULs where the capture is read, or at capture time:

```bash
tr -d '\000' < audit/probe2.txt > audit/probe2.clean && mv audit/probe2.clean audit/probe2.txt
```

For the next run, put the `tr` in the collection command (`... | tr -d '\000'`)
rather than after the file already looks binary. Do not re-run the remote
collection, and do not assume the SSH session or the script failed — only that
one section contained NULs.