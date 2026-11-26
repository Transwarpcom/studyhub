import WidgetKit
import SwiftUI

// MARK: - 数据

struct HubEntry: TimelineEntry {
    var date: Date
    var due: Int
    var today: Int
    var wrong: Int
    var streak: Int
}

struct Provider: TimelineProvider {
    private func read(_ key: String) -> Int {
        let d = UserDefaults(suiteName: "group.cn.medwarp.studyhub") ?? .standard
        return d.integer(forKey: key)
    }

    private func current() -> HubEntry {
        HubEntry(date: Date(), due: read("widget.due"), today: read("widget.today"),
                 wrong: read("widget.wrong"), streak: read("widget.streak"))
    }

    func placeholder(in context: Context) -> HubEntry {
        HubEntry(date: Date(), due: 3, today: 12, wrong: 5, streak: 4)
    }

    func getSnapshot(in context: Context, completion: @escaping (HubEntry) -> Void) {
        completion(current())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<HubEntry>) -> Void) {
        let next = Calendar.current.date(byAdding: .minute, value: 30, to: Date()) ?? Date()
        completion(Timeline(entries: [current()], policy: .after(next)))
    }
}

// MARK: - 视图

struct HubWidgetView: View {
    @Environment(\.widgetFamily) private var family

    var entry: HubEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 4) {
                Image(systemName: "book.closed.fill").font(.caption2)
                Text("学习台").font(.caption2.weight(.semibold))
                Spacer()
                Text("\(entry.streak) 天").font(.caption2)
            }
            .foregroundColor(.secondary)

            if family == .systemSmall {
                big("\(entry.due)", "待复习")
                Text("今日 \(entry.today) 题 · 错题 \(entry.wrong)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            } else {
                HStack(spacing: 10) {
                    cell("\(entry.due)", "待复习", .orange)
                    cell("\(entry.today)", "今日答题", .blue)
                    cell("\(entry.wrong)", "错题", .red)
                }
            }
        }
        .padding(4)
    }

    private func big(_ v: String, _ t: String) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(v).font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundColor(.orange)
            Text(t).font(.caption2).foregroundColor(.secondary)
        }
    }

    private func cell(_ v: String, _ t: String, _ c: Color) -> some View {
        VStack(spacing: 1) {
            Text(v).font(.system(size: 22, weight: .bold, design: .rounded)).foregroundColor(c)
            Text(t).font(.system(size: 9)).foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - 入口

@main
struct StudyHubWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "StudyHubWidget", provider: Provider()) { entry in
            HubWidgetView(entry: entry)
        }
        .configurationDisplayName("学习台")
        .description("今日待复习、已答题和错题数")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
