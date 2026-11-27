# A package name is not an app name

Symptom: I identified `com.ss.android.yumme.video` as 西瓜视频 (Xigua Video) and uninstalled it on that basis; it is actually 青桃 / **抖音精选** (Douyin Featured), and 西瓜视频 is `com.ss.android.article.video`. The user lost the app they wanted, and the error looked like *their* memory being wrong.

Why the shortcut failed: ByteDance ships several apps on one code base, so the manifest activity `com.ss.android.ugc.aweme.splash.SplashActivity` appears under 抖音, 抖音精选, 西瓜视频 and their lite builds. Package prefix, activity class and `installerPackageName` all fail to distinguish them. `dumpsys package` never prints a human label.

Check before acting — any one is enough:

- `curl -s https://apkpure.com/<pkg>` or `https://www.apkmirror.com/...` and read the title, or `web_search "<pkg> 包名 应用"`;
- pull `base.apk` and read `application android:label` from the resources (`aapt2 dump badging base.apk`);
- ask the owner to look at the icon label — cheapest of all, and it settles the question.

Rule: never delete, disable or report on an app based only on its package name. Name the evidence in the same breath ("com.x = App Y, per <url>") so the mapping can be challenged before it costs something.

Related: `20261127-adb-devices-empty-vendor-interface.md` (same session, adb setup).
