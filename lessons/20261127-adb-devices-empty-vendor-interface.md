# `adb devices` empty while `lsusb` shows the phone: the port is not in ADB mode

**Symptom**

- Phone is plugged in, `lsusb` lists it (Huawei: `12d1:107d`), the kernel even binds storage (interface `8/6` = SCSI), but `adb devices` prints only `List of devices attached` and nothing else.
- No permission error, no `unauthorized` — the device simply is not there.

**Why**

`12d1:107d` exposes interfaces `255/255`, `8/6` (mass storage) and `255/72/1`, i.e. HDB/MTP mode. **None of them is the ADB interface (class `ff`, subclass `42`, protocol `01`)**, so `adb` has nothing to connect to. Selecting "file transfer" on the phone only changes the storage interface; it does not add ADB.

**Fix**

Open 设置 → 系统和更新 → 开发人员选项 → **USB 调试** (turning on "开发者选项" alone is not enough). The phone re-enumerates, `lsusb` shows the ADB interface, and `adb devices` then lists `<serial>\tdevice`. First connection may need "允许 USB 调试" on the phone.

**Check that catches it next time**

```bash
lsusb -d <vid>:<pid> -v 2>/dev/null | grep -E 'bInterfaceClass|bInterfaceSubClass|bInterfaceProtocol'
adb devices -l
```

`bInterfaceClass 255 bInterfaceSubClass 42 bInterfaceProtocol 1` must appear before `adb devices` can list anything. If it is missing, the problem is on the phone's side (USB mode / 调试开关), not with `udev`, ACLs or the adb binary — do not chase `/dev/bus/usb` permissions.

**Also worth knowing**

- `adb shell` on a Huawei/HarmonyOS device works fine for read-only diagnostics without root (`dumpsys`, `/proc`, `logcat`). `su` is not needed and not available.
- `dumpsys activity processes` is the cheapest source of per-process PSS plus swap (`lastPss=` / `lastSwapPss=`); parse it instead of `dumpsys meminfo`, which truncates at the app level.

## Measuring app start time: check load first

`am start -W` reports whatever the device is doing at that moment, including work you caused. On a Huawei phone freshly plugged in after uninstalling apps, WeChat cold start read **3376 ms and 4210 ms**; five seconds later the same test read **962 ms** and **1397 ms** (baseline 1671 ms). `/proc/loadavg` at the bad readings was **20.39** — the system was still re-optimising packages and scanning media.

Before trusting any `am start -W` number, read `/proc/loadavg` and `dumpsys cpuinfo | head`; discard and repeat if the 1-minute load is above ~2 on an 8-core phone. Report the best of two clean runs, not the first one.
