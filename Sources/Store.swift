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

    func record(lessonId: String, cardId: String, correct: Bool) {
        progress["\(lessonId)|\(cardId)"] = correct
        saveProgress()
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
