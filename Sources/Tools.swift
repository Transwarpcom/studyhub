import Foundation
import AVFoundation
import UserNotifications
import SwiftUI

// MARK: - 朗读

@MainActor
final class Speaker: ObservableObject {
    static let shared = Speaker()
    private let synth = AVSpeechSynthesizer()
    @Published var speaking = false

    func toggle(_ text: String) {
        if speaking {
            stop()
        } else {
            speak(text)
        }
    }

    func speak(_ text: String) {
        stop()
        let clean = Speaker.plain(text)
        guard !clean.isEmpty else { return }
        let u = AVSpeechUtterance(string: clean)
        u.voice = AVSpeechSynthesisVoice(language: "zh-CN")
        u.rate = 0.48
        u.pitchMultiplier = 1.0
        synth.speak(u)
        speaking = true
        // 播完自动复位
        DispatchQueue.main.asyncAfter(deadline: .now() + max(3, Double(clean.count) * 0.16)) { [weak self] in
            if self?.synth.isSpeaking == false { self?.speaking = false }
        }
    }

    func stop() {
        synth.stopSpeaking(at: .immediate)
        speaking = false
    }

    /// 把讲解卡拼成纯文本（去掉 LaTeX、markdown 符号）
    static func plain(_ s: String) -> String {
        var t = s
        t = t.replacingOccurrences(of: "$$", with: " ")
        t = t.replacingOccurrences(of: "$", with: " ")
        t = t.replacingOccurrences(of: "\\dfrac", with: "")
        t = t.replacingOccurrences(of: "\\frac", with: "")
        t = t.replacingOccurrences(of: "\\", with: " ")
        t = t.replacingOccurrences(of: "#", with: " ")
        t = t.replacingOccurrences(of: "*", with: " ")
        t = t.replacingOccurrences(of: "`", with: " ")
        t = t.replacingOccurrences(of: "|", with: " ")
        t = t.replacingOccurrences(of: ">", with: " ")
        t = t.replacingOccurrences(of: "[", with: " ")
        t = t.replacingOccurrences(of: "]", with: " ")
        t = t.replacingOccurrences(of: "{", with: " ")
        t = t.replacingOccurrences(of: "}", with: " ")
        t = t.replacingOccurrences(of: "_", with: " ")
        t = t.replacingOccurrences(of: "  ", with: " ")
        return t.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// 从一节里取要读的文本
    static func text(of lesson: Lesson) -> String {
        var out: [String] = [lesson.title]
        for c in lesson.cards where c.type == "lecture" {
            if let t = c.title { out.append(t) }
            if let md = c.md { out.append(md) }
        }
        return out.joined(separator: "。\n")
    }
}

// MARK: - 每日提醒

enum Reminder {
    static let keyEnabled = "hub.reminder.enabled"
    static let keyHour = "hub.reminder.hour"
    static let keyMinute = "hub.reminder.minute"

    static var enabled: Bool {
        get { UserDefaults.standard.bool(forKey: keyEnabled) }
        set { UserDefaults.standard.set(newValue, forKey: keyEnabled) }
    }
    static var hour: Int {
        get { UserDefaults.standard.object(forKey: keyHour) as? Int ?? 20 }
        set { UserDefaults.standard.set(newValue, forKey: keyHour) }
    }
    static var minute: Int {
        get { UserDefaults.standard.object(forKey: keyMinute) as? Int ?? 0 }
        set { UserDefaults.standard.set(newValue, forKey: keyMinute) }
    }

    static func apply() {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: ["studyhub.daily"])
        guard enabled else { return }
        center.requestAuthorization(options: [.alert, .sound, .badge]) { ok, _ in
            guard ok else { return }
            let c = UNMutableNotificationContent()
            c.title = "该复习了"
            c.body = "打开学习台，先把到期的复习题过一遍"
            c.sound = .default
            var comps = DateComponents()
            comps.hour = hour
            comps.minute = minute
            let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: true)
            let req = UNNotificationRequest(identifier: "studyhub.daily", content: c, trigger: trigger)
            center.add(req)
        }
    }

    static func disable() {
        enabled = false
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["studyhub.daily"])
    }
}

// MARK: - 学习报告

enum ReportBuilder {
    static func text(store: Store) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        var lines: [String] = []
        lines.append("学习台 · 学习报告")
        lines.append("生成时间：\(f.string(from: Date()))")
        lines.append("")
        lines.append("连续学习：\(store.streakDays) 天")
        lines.append("今日答题：\(store.todayStat.answered) 题")
        lines.append("累计答题：\(store.totalAnswered) 题")
        let rate = store.totalAnswered > 0 ? store.totalCorrect * 100 / store.totalAnswered : 0
        lines.append("累计正确率：\(rate)%")
        lines.append("错题：\(store.wrongs.count) 道")
        lines.append("待复习：\(store.dueReviews.count) 道")
        lines.append("已缓存：\(store.cachedLessonCount) 节")
        lines.append("")

        // 最近 7 天
        lines.append("最近 7 天：")
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        var d = Date()
        for _ in 0..<7 {
            let key = df.string(from: d)
            if let st = store.days[key], st.answered > 0 {
                let r = st.correct * 100 / max(st.answered, 1)
                lines.append("  \(key)  答 \(st.answered) 题，正确率 \(r)%")
            } else {
                lines.append("  \(key)  未学习")
            }
            d = d.addingTimeInterval(-86400)
        }
        lines.append("")

        // 错题分布 top 5
        if !store.wrongs.isEmpty {
            var cnt: [String: Int] = [:]
            for w in store.wrongs { cnt[w.lessonTitle, default: 0] += 1 }
            lines.append("错题最多的章节：")
            for (k, v) in cnt.sorted(by: { $0.value > $1.value }).prefix(5) {
                lines.append("  \(k)：\(v) 道")
            }
        }
        return lines.joined(separator: "\n")
    }
}
