import Foundation
import SwiftUI

@MainActor
final class Store: ObservableObject {
    @Published var manifest: Manifest?
    @Published var loading = false
    @Published var lastError: String?
    @Published var lastSync: Date?
    @Published var progress: [String: Bool] = [:]     // "lessonId|cardId" -> 是否正确
    @Published var replies: [Lesson] = []
    @Published var uploads: [UploadRecord] = []
    @Published var wrongs: [WrongItem] = []
    @Published var days: [String: DayStat] = [:]

    // 批量缓存
    @Published var downloading = false
    @Published var dlDone = 0
    @Published var dlTotal = 0
    @Published var dlFailed = 0

    // 阅读器字号
    @Published var fontSize: Double = UserDefaults.standard.object(forKey: "hub.fontSize") as? Double ?? 17

    let client = HubClient.shared
    private var lessons: [String: Lesson] = [:]

    init() {
        loadLocal()
    }

    // MARK: 本地

    func loadLocal() {
        if let d = client.loadCache(name: "manifest"),
           let m = try? JSONDecoder().decode(Manifest.self, from: d) {
            manifest = m
        }
        if let d = UserDefaults.standard.data(forKey: "hub.progress"),
           let p = try? JSONDecoder().decode([String: Bool].self, from: d) {
            progress = p
        }
        if let d = UserDefaults.standard.data(forKey: "hub.uploads"),
           let u = try? JSONDecoder().decode([UploadRecord].self, from: d) {
            uploads = u
        }
        if let d = UserDefaults.standard.data(forKey: "hub.wrongs"),
           let w = try? JSONDecoder().decode([WrongItem].self, from: d) {
            wrongs = w
        }
        if let d = UserDefaults.standard.data(forKey: "hub.days"),
           let x = try? JSONDecoder().decode([String: DayStat].self, from: d) {
            days = x
        }
        if let t = UserDefaults.standard.object(forKey: "hub.lastSync") as? Date {
            lastSync = t
        }
    }

    private func saveProgress() {
        if let d = try? JSONEncoder().encode(progress) {
            UserDefaults.standard.set(d, forKey: "hub.progress")
        }
    }

    private func saveUploads() {
        if let d = try? JSONEncoder().encode(uploads) {
            UserDefaults.standard.set(d, forKey: "hub.uploads")
        }
    }

    private func saveWrongs() {
        if let d = try? JSONEncoder().encode(wrongs) {
            UserDefaults.standard.set(d, forKey: "hub.wrongs")
        }
    }

    private func saveDays() {
        if let d = try? JSONEncoder().encode(days) {
            UserDefaults.standard.set(d, forKey: "hub.days")
        }
    }

    // MARK: 批量缓存

    func flatten(_ nodes: [Node]) -> [Node] {
        var out: [Node] = []
        for n in nodes {
            if n.kind == "folder" {
                out += flatten(n.children ?? [])
            } else {
                out.append(n)
            }
        }
        return out
    }

    var allLessonNodes: [Node] {
        flatten(manifest?.tree ?? [])
    }

    /// 下载整棵树（已缓存的直接跳过）
    func downloadAll() async {
        guard !downloading else { return }
        let list = allLessonNodes
        guard !list.isEmpty else { return }
        downloading = true
        dlTotal = list.count
        dlDone = 0
        dlFailed = 0
        for n in list {
            if cachedLesson(node: n) != nil { dlDone += 1; continue }
            do { _ = try await loadLesson(node: n) } catch { dlFailed += 1 }
            dlDone += 1
        }
        downloading = false
    }

    /// 下载某一棵子树
    func download(_ node: Node) async {
        guard !downloading else { return }
        let list = node.kind == "folder" ? flatten(node.children ?? []) : [node]
        guard !list.isEmpty else { return }
        downloading = true
        dlTotal = list.count
        dlDone = 0
        dlFailed = 0
        for n in list {
            if cachedLesson(node: n) != nil { dlDone += 1; continue }
            do { _ = try await loadLesson(node: n) } catch { dlFailed += 1 }
            dlDone += 1
        }
        downloading = false
    }

    var cachedLessonCount: Int {
        let fm = FileManager.default
        guard let items = try? fm.contentsOfDirectory(at: client.cacheDir, includingPropertiesForKeys: nil) else { return 0 }
        return items.filter { $0.lastPathComponent.hasPrefix("lesson_") }.count
    }

    var cacheBytes: Int64 {
        let fm = FileManager.default
        guard let items = try? fm.contentsOfDirectory(at: client.cacheDir,
                                                      includingPropertiesForKeys: [.fileSizeKey]) else { return 0 }
        var total: Int64 = 0
        for u in items {
            if let v = try? u.resourceValues(forKeys: [.fileSizeKey]), let s = v.fileSize {
                total += Int64(s)
            }
        }
        return total
    }

    func clearLessonCache() {
        let fm = FileManager.default
        guard let items = try? fm.contentsOfDirectory(at: client.cacheDir, includingPropertiesForKeys: nil) else { return }
        for u in items where u.lastPathComponent.hasPrefix("lesson_") {
            try? fm.removeItem(at: u)
        }
        lessons.removeAll()
    }

    // MARK: 统计

    var totalAnswered: Int { progress.count }
    var totalCorrect: Int { progress.values.filter { $0 }.count }

    /// 连续学习天数（今天没答就从昨天往前数）
    var streakDays: Int {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        var streak = 0
        var d = Date()
        var skippedToday = false
        for _ in 0..<400 {
            let key = f.string(from: d)
            if let st = days[key], st.answered > 0 {
                streak += 1
                d = d.addingTimeInterval(-86400)
                skippedToday = true
            } else if !skippedToday {
                d = d.addingTimeInterval(-86400)
                skippedToday = true
            } else {
                break
            }
        }
        return streak
    }

    var todayStat: DayStat {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        return days[f.string(from: Date())] ?? DayStat(day: "", answered: 0, correct: 0)
    }

    func setFontSize(_ v: Double) {
        fontSize = v
        UserDefaults.standard.set(v, forKey: "hub.fontSize")
    }

    // MARK: 同步

    func bootstrap() async {
        if manifest == nil && !loading {
            await refresh()
        }
    }

    func refresh() async {
        guard !loading else { return }
        loading = true
        defer { loading = false }
        do {
            let data = try await client.getRaw("/manifest")
            let m = try JSONDecoder().decode(Manifest.self, from: data)
            manifest = m
            client.saveCache(data, name: "manifest")
            let now = Date()
            lastSync = now
            UserDefaults.standard.set(now, forKey: "hub.lastSync")
            lastError = nil
            await loadReplies()
        } catch {
            lastError = error.localizedDescription
        }
    }

    func loadReplies() async {
        do {
            let data = try await client.getRaw("/replies")
            let r = try JSONDecoder().decode(ReplyList.self, from: data)
            replies = r.replies
            client.saveCache(data, name: "replies")
        } catch {
            if let d = client.loadCache(name: "replies"),
               let r = try? JSONDecoder().decode(ReplyList.self, from: d) {
                replies = r.replies
            }
        }
    }

    // MARK: 章节

    func loadLesson(node: Node) async throws -> Lesson {
        let key = node.bundle ?? node.id
        if let cached = lessons[key] { return cached }

        let path = "/lesson?" + queryFor(key)
        if let data = try? await client.getRaw(path) {
            let lesson = try JSONDecoder().decode(Lesson.self, from: data)
            lessons[key] = lesson
            client.saveCache(data, name: "lesson_" + key)
            return lesson
        }
        // 离线兜底
        if let d = client.loadCache(name: "lesson_" + key),
           let lesson = try? JSONDecoder().decode(Lesson.self, from: d) {
            lessons[key] = lesson
            return lesson
        }
        throw HubError.decode("这一节还没有同步过，连上网络再试")
    }

    private func queryFor(_ key: String) -> String {
        let allowed = CharacterSet.urlQueryAllowed
        let enc = key.addingPercentEncoding(withAllowedCharacters: allowed) ?? key
        return "id=" + enc
    }

    func cachedLesson(node: Node) -> Lesson? {
        let key = node.bundle ?? node.id
        if let l = lessons[key] { return l }
        if let d = client.loadCache(name: "lesson_" + key),
           let l = try? JSONDecoder().decode(Lesson.self, from: d) {
            lessons[key] = l
            return l
        }
        return nil
    }

    // MARK: 答题

    func record(lessonId: String, lessonTitle: String, cardId: String,
                correct: Bool, preview: String) {
        let key = "\(lessonId)|\(cardId)"
        progress[key] = correct
        saveProgress()

        // 错题本：答错加入，答对移除
        if correct {
            wrongs.removeAll { $0.id == key }
        } else {
            wrongs.removeAll { $0.id == key }
            wrongs.insert(WrongItem(id: key, lessonId: lessonId, lessonTitle: lessonTitle,
                                    cardId: cardId, preview: preview, ts: Date()), at: 0)
            if wrongs.count > 300 { wrongs = Array(wrongs.prefix(300)) }
        }
        saveWrongs()

        // 按天统计
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        let day = f.string(from: Date())
        var st = days[day] ?? DayStat(day: day, answered: 0, correct: 0)
        st.answered += 1
        if correct { st.correct += 1 }
        days[day] = st
        saveDays()
    }

    func stats(lesson: Lesson) -> (answered: Int, correct: Int, total: Int) {
        var answered = 0
        var correct = 0
        var total = 0
        for c in lesson.cards where c.type != "lecture" {
            total += 1
            if let v = progress["\(lesson.id)|\(c.id)"] {
                answered += 1
                if v { correct += 1 }
            }
        }
        return (answered, correct, total)
    }

    func progressDict(lesson: Lesson) -> [String: Bool] {
        var d: [String: Bool] = [:]
        for c in lesson.cards {
            if let v = progress["\(lesson.id)|\(c.id)"] { d[c.id] = v }
        }
        return d
    }

    // MARK: 上传

    func upload(data: Data, filename: String, mime: String, note: String) async throws -> String {
        let resp = try await client.upload(data: data, filename: filename, mime: mime, note: note)
        if resp.ok {
            let rec = UploadRecord(id: resp.id ?? UUID().uuidString,
                                   title: filename,
                                   created: Date(),
                                   status: "已提交")
            uploads.insert(rec, at: 0)
            if uploads.count > 50 { uploads = Array(uploads.prefix(50)) }
            saveUploads()
            return resp.id ?? ""
        } else {
            throw HubError.decode(resp.error ?? "上传失败")
        }
    }
}
