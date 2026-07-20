solutions = [
  {
    "name": "StealthBrowser",
    "url": "https://chromium.googlesource.com/chromium/src.git",
    "deps_file": "DEPS",
    "managed": False,
    "custom_deps": {
      "src/third_party/stealth-adblocker": "https://github.com/itriedcoding/stealth-adblocker.git",
    },
  },
]
