# -*- coding: utf-8 -*-
"""project.yml：加 Widget target + App Group entitlements；主 App 写共享数据"""
import io

P = r"C:/Users/chong/Documents/studyhub/project.yml"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s 命中 %d" % (tag, n)
    s = s.replace(old, new)
    print("  ok", tag)


# 主 target：entitlements + 依赖 Widget
sub("""    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: cn.medwarp.studyhub""",
    """    dependencies:
      - target: StudyHubWidget
    settings:
      base:
        CODE_SIGN_ENTITLEMENTS: StudyHub.entitlements
        PRODUCT_BUNDLE_IDENTIFIER: cn.medwarp.studyhub""", "主 target")

# 追加 Widget target
sub("""schemes:
  StudyHub:""",
    """  StudyHubWidget:
    type: app-extension
    platform: iOS
    sources:
      - path: Widget
    info:
      path: Widget/Info.plist
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: cn.medwarp.studyhub.widget
        PRODUCT_NAME: StudyHubWidget
        CODE_SIGN_ENTITLEMENTS: Widget/Widget.entitlements
        SKIP_INSTALL: "YES"
        TARGETED_DEVICE_FAMILY: "1,2"

schemes:
  StudyHub:""", "Widget target")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written project.yml")
