[app]

title = Schedule
package.name = schedule
package.domain = org.schedule

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,atlas

version = 0.1.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.accept_sdk_license = True

android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
