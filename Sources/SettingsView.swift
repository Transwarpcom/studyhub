import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var store: Store

    @State private var base = HubClient.shared.baseURL
    @State private var token = HubClient.shared.token
    @State private var hint: String?

    var body: some View {
        NavigationStack {
            Form {
                Section("服务器") {
                    TextField("接口地址", text: $base)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                        .font(.footnote)
                    SecureField("访问口令", text: $token)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    Button("保存并同步") {
                        HubClient.shared.baseURL = base.trimmingCharacters(in: .whitespacesAndNewlines)
                        HubClient.shared.token = token.trimmingCharacters(in: .whitespacesAndNewlines)
                        hint = "已保存"
                        Task { await store.refresh() }
                    }
                    if let hint {
                        Text(hint).font(.caption).foregroundColor(.secondary)
                    }
                }

                Section("离线缓存") {
                    if store.downloading {
                        VStack(alignment: .leading, spacing: 8) {
                            ProgressView(value: Double(store.dlDone),
                                         total: Double(max(store.dlTotal, 1)))
                            Text("正在下载 \(store.dlDone)/\(store.dlTotal) 节"
                                 + (store.dlFailed > 0 ? "，失败 \(store.dlFailed)" : ""))
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.vertical, 4)
                    } else {
                        Button {
                            Task { await store.downloadAll() }
                        } label: {
                            Label("下载全部内容（\(store.allLessonNodes.count) 节）",
                                  systemImage: "arrow.down.circle.fill")
                        }
                    }
                    LabeledContent("已缓存", value: "\(store.cachedLessonCount) 节 · \(bytesText(store.cacheBytes))")
                    Button("清空离线缓存（保留答题记录）") {
                        store.clearLessonCache()
                        hint = "缓存已清"
                    }
                }

                Section("阅读") {
                    HStack {
                        Text("字号")
                        Slider(value: Binding(get: { store.fontSize },
                                              set: { store.setFontSize($0) }),
                               in: 14...22, step: 1)
                        Text("\(Int(store.fontSize))")
                            .font(.footnote.monospacedDigit())
                            .foregroundColor(.secondary)
                            .frame(width: 26, alignment: .trailing)
                    }
                    Picker("主题", selection: Binding(get: { store.theme },
                                                    set: { store.setTheme($0) })) {
                        Text("跟随系统").tag("auto")
                        Text("浅色").tag("light")
                        Text("深色").tag("dark")
                    }
                    .pickerStyle(.segmented)
                }

                Section("学习统计") {
                    LabeledContent("连续学习", value: "\(store.streakDays) 天")
                    LabeledContent("今日答题", value: "\(store.todayStat.answered) 题")
                    LabeledContent("累计答题", value: "\(store.totalAnswered) 题")
                    LabeledContent("累计正确率", value: rateText)
                    LabeledContent("错题", value: "\(store.wrongs.count) 道")
                }

                Section("状态") {
                    LabeledContent("内容版本", value: store.manifest.map { "v\($0.version)" } ?? "—")
                    LabeledContent("上次同步", value: dateText(store.lastSync))
                    LabeledContent("已答题目", value: "\(store.progress.count)")
                    LabeledContent("缓存章节", value: "\(cacheCount())")
                    if let e = store.lastError {
                        Text(e).font(.footnote).foregroundColor(.orange)
                    }
                }

                Section {
                    Button("重新同步内容") {
                        Task { await store.refresh() }
                    }
                    Button("清空缓存（保留答题记录）") {
                        HubClient.shared.clearCache()
                        store.loadLocal()
                        hint = "缓存已清"
                    }
                }

                Section("关于") {
                    LabeledContent("版本", value: "1.0.0")
                    Text("学习台 · 高数 / 大学英语\n课程按文件夹组织，支持公式、矢量图、单选、多选、判断、填空、简答。内容由 Hermes 远程下发，读过的章节离线可看。")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("设置")
        }
    }

    private func dateText(_ d: Date?) -> String {
        guard let d else { return "从未" }
        let f = DateFormatter()
        f.dateFormat = "MM-dd HH:mm"
        return f.string(from: d)
    }

    private func cacheCount() -> Int {
        let fm = FileManager.default
        guard let items = try? fm.contentsOfDirectory(at: HubClient.shared.cacheDir,
                                                      includingPropertiesForKeys: nil) else { return 0 }
        return items.filter { $0.lastPathComponent.hasPrefix("lesson_") }.count
    }

    private var rateText: String {
        let a = store.totalAnswered
        guard a > 0 else { return "—" }
        return "\(store.totalCorrect * 100 / a)%"
    }

    private func bytesText(_ b: Int64) -> String {
        let f = ByteCountFormatter()
        f.countStyle = .file
        return f.string(fromByteCount: b)
    }
}
