# GitHub Releases are ~25 KB/s here, and a timed-out download leaves a plausible file

**First, try the proxy.** `bash -c 'source ~/.proxyrc; curl -L -o <file> <url>'`
moved the same kind of `codeload.github.com` tarball from 628 KB/s (cut off) to
5.2 MB/s (complete) on 2026-11-15. See
`lessons/20261115-foreign-host-network-use-proxyrc.md`. The rest of this note
applies when the proxy is down or the asset is too large even through it.

**Signal.** A `curl -m 300` of a 49 MB release asset ends with exit code 28
(timeout) and a 7 MB file; a `-m 600` retry of a 38 MB model reaches 15 MB.
`ls -l` shows a real file, so the next step (`unzip -l`, `tar xf`) runs on a
truncated archive. Sizes to expect: ~20–40 KB/s, i.e. a 38 MB tarball needs
~20 minutes and a 49 MB AAR much longer.

**Rule.** Before extracting an archive fetched from a release, compare its size
with the asset size from the GitHub API — `curl -s
https://api.github.com/repos/<owner>/<repo>/releases/latest` and check
`assets[].size`. A truncated `.bz2` fails loudly on `tar xf`; a truncated `.zip`/
`.aar` can partially list, which is worse.

**What works instead.** The Aliyun PyPI mirror moves at ~2.3 MB/s
(`--index-url https://mirrors.aliyun.com/pypi/simple/`), and `python3.13` has
sherpa-onnx cp313 wheels there. Hugging Face mirrors and ModelScope are
reachable, but check that the repo actually contains the weights: the
`sherpa-onnx-kws-*` copy on hf-mirror is a WASM build (`install/bin/wasm/...`),
not the `.onnx` files. For sherpa-onnx the GitHub Release is the only source,
so a 38–49 MB spike is not a one-turn operation on this host.

**And.** `developer.android.com` is unreachable from this machine (`curl` exit
28, `web_fetch` TypeError `fetch failed`), so Android platform rules cannot be
cited from the source page here. Read them from the installed SDK
(`$ANDROID_HOME/platforms/android-*/`) or the device, and label platform
behaviour as unverified rather than quoting numbers from memory.

