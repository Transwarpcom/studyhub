# -*- coding: utf-8 -*-
"""设置页加「答题前可以看解析」开关"""
import io

P = r"C:/Users/chong/Documents/studyhub/Sources/SettingsView.swift"
s = io.open(P, encoding="utf-8").read()

old_state = "    @State private var hint: String?"
assert s.count(old_state) == 1, "hint 声明命中 %d" % s.count(old_state)
s = s.replace(old_state, old_state + "\n    @AppStorage(\"hub.allowPeek\") private var allowPeek = true")

old = """                    .pickerStyle(.segmented)
                }

                Section("学习统计") {"""
new = """                    .pickerStyle(.segmented)
                }

                Section {
                    Toggle("答题前可以看解析", isOn: $allowPeek)
                    Text("打开后每题都有「先看解析」按钮。看了解析的题不算答对，直接记入待复习与错题本，正确率不受影响。")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                } header: {
                    Text("答题")
                }

                Section("学习统计") {"""
assert s.count(old) == 1, "Section 学习统计 命中 %d" % s.count(old)
s = s.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written", P)
