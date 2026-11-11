import SwiftUI

/// 错题本：按错题所属章节分组，点进去重做
struct WrongBookView: View {
    @EnvironmentObject var store: Store
    @State private var active: WrongItem?

    var body: some View {
        NavigationStack {
            List {
                if store.wrongs.isEmpty {
                    Section {
                        VStack(spacing: 10) {
                            Image(systemName: "checkmark.seal.fill")
                                .font(.system(size: 34))
                                .foregroundColor(.green)
                            Text("没有错题").font(.headline)
                            Text("答错的选择、填空、判断会自动进这里；重做答对就自动移除。")
                                .font(.footnote)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 30)
                    }
                } else {
                    Section {
                        HStack {
                            Text("共 \(store.wrongs.count) 道").font(.headline)
                            Spacer()
                            Button("清空") {
                                store.wrongs = []
                                if let d = try? JSONEncoder().encode([WrongItem]()) {
                                    UserDefaults.standard.set(d, forKey: "hub.wrongs")
                                }
                            }
                            .font(.footnote)
                            .foregroundColor(.red)
                        }
                    }

                    // 按章节分组
                    ForEach(groups, id: \.key) { g in
                        Section(g.title) {
                            ForEach(g.items) { w in
                                Button {
                                    active = w
                                } label: {
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text(w.preview.isEmpty ? w.cardId : w.preview)
                                            .font(.subheadline)
                                            .foregroundColor(.primary)
                                            .lineLimit(2)
                                            .multilineTextAlignment(.leading)
                                        Text(timeText(w.ts))
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                    .padding(.vertical, 2)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("错题本")
            .refreshable { await store.loadReplies() }
            .sheet(item: $active) { w in
                WrongDetailView(item: w)
            }
        }
    }

    private var groups: [(key: String, title: String, items: [WrongItem])] {
        var dict: [String: [WrongItem]] = [:]
        for w in store.wrongs { dict[w.lessonId, default: []].append(w) }
        return dict.map { (k, v) in
            (key: k, title: v.first?.lessonTitle ?? k, items: v)
        }
        .sorted { $0.title < $1.title }
    }

    private func timeText(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "MM-dd HH:mm"
        return f.string(from: d)
    }
}

/// 打开错题所属章节，滚动到那一题（简化：直接打开整节）
struct WrongDetailView: View {
    let item: WrongItem
    @EnvironmentObject var store: Store
    @State private var lesson: Lesson?
    @State private var error: String?

    var body: some View {
        NavigationStack {
            Group {
                if let lesson {
                    ReaderWebView(lesson: lesson)
                        .ignoresSafeArea(edges: .bottom)
                } else if let error {
                    VStack(spacing: 12) {
                        Image(systemName: "wifi.exclamationmark")
                            .font(.system(size: 30)).foregroundColor(.orange)
                        Text(error).font(.footnote).multilineTextAlignment(.center).padding(.horizontal, 30)
                    }
                } else {
                    ProgressView("加载中…")
                }
            }
            .navigationTitle(item.lessonTitle)
            .navigationBarTitleDisplayMode(.inline)
            .task {
                let node = Node(id: item.lessonId, title: item.lessonTitle, icon: nil,
                                kind: "lesson", summary: nil, children: nil,
                                bundle: item.lessonId, badge: nil)
                do { lesson = try await store.loadLesson(node: node) }
                catch { self.error = error.localizedDescription }
            }
        }
    }
}
