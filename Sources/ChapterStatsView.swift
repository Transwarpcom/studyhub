import SwiftUI

// MARK: - 各章掌握度

struct ChapterStatsView: View {
    @EnvironmentObject var store: Store
    @State private var stats: [ChapterStat] = []
    @State private var busy = false

    var body: some View {
        List {
            if busy && stats.isEmpty {
                Section {
                    HStack { Spacer(); ProgressView("统计中…"); Spacer() }
                        .padding(.vertical, 30)
                }
            } else if stats.isEmpty {
                Section {
                    Text("还没有内容，先下拉刷新课程")
                        .foregroundColor(.secondary)
                }
            } else {
                Section {
                    HStack(spacing: 16) {
                        metric("\(stats.reduce(0) { $0 + $1.total })", "总题数")
                        metric("\(stats.reduce(0) { $0 + $1.answered })", "已做")
                        metric("\(stats.reduce(0) { $0 + $1.due })", "待复习")
                        Spacer()
                    }
                    .padding(.vertical, 4)
                }

                ForEach(stats) { st in
                    Section(st.title) {
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text("\(st.correct)/\(st.answered) 答对")
                                    .font(.footnote)
                                Spacer()
                                Text("共 \(st.total) 题")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            ProgressView(value: st.progress)
                            HStack(spacing: 12) {
                                tag("待复习 \(st.due)", .orange, st.due > 0)
                                tag("错题 \(st.wrong)", .red, st.wrong > 0)
                                if st.answered > 0 {
                                    Text("正确率 \(Int(st.accuracy * 100))%")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                                Spacer()
                            }
                        }
                        .padding(.vertical, 2)
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle("各章掌握度")
        .navigationBarTitleDisplayMode(.inline)
        .refreshable { await load() }
        .task { await load() }
    }

    private func metric(_ v: String, _ t: String) -> some View {
        VStack(spacing: 2) {
            Text(v).font(.headline.monospacedDigit())
            Text(t).font(.caption2).foregroundColor(.secondary)
        }
    }

    private func tag(_ text: String, _ color: Color, _ on: Bool) -> some View {
        Text(text)
            .font(.caption2)
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(on ? color.opacity(0.15) : Color.secondary.opacity(0.1))
            .foregroundColor(on ? color : .secondary)
            .clipShape(Capsule())
    }

    private func load() async {
        busy = true
        let s = await store.chapterStats()
        await MainActor.run {
            stats = s
            busy = false
        }
    }
}
