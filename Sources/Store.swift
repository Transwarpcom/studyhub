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
    @Published var reviews: [String: ReviewItem] = [:]
    @Published var notes: [String: String] = [:]          // lessonId -> 笔记
    @Published var favorites: Set<String> = []            // 收藏的 lessonId
    @Published var positions: [String: Double] = [:]      // lessonId -> 阅读位置

    // 批量缓存
    @Published var downloading = false
    @Published var dlDone = 0
    @Published var dlTotal = 0
    @Published var dlFailed = 0

    // 阅读器字号
    @Published var fontSize: Double = UserDefaults.standard.object(forKey: "hub.fontSize") as? Double ?? 17
    // 阅读器主题：auto / light / dark
    @Published var theme: String = UserDefaults.standard.string(forKey: "hub.theme") ?? "auto"

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
        if let d = UserDefaults.standard.data(forKey: "hub.reviews"),
           let r = try? JSONDecoder().decode([String: ReviewItem].self, from: d) {
            reviews = r
        }
        if let d = UserDefaults.standard.data(forKey: "hub.notes"),
           let n = try? JSONDecoder().decode([String: String].self, from: d) {
            notes = n
        }
        if let a = UserDefaults.standard.array(forKey: "hub.favorites") as? [String] {
            favorites = Set(a)
        }
        if let d = UserDefaults.standard.data(forKey: "hub.positions"),
           let p = try? JSONDecoder().decode([String: Double].self, from: d) {
            positions = p
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

    private func saveReviews() {
        if let d = try? JSONEncoder().encode(reviews) {
            UserDefaults.standard.set(d, forKey: "hub.reviews")
        }
    }

    // MARK: 笔记 / 收藏 / 阅读位置

    func saveNotes() {
        if let d = try? JSONEncoder().encode(notes) {
            UserDefaults.standard.set(d, forKey: "hub.notes")
        }
    }

    func setNote(_ text: String, for lessonId: String) {
        if text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            notes.removeValue(forKey: lessonId)
        } else {
            notes[lessonId] = text
        }
        saveNotes()
    }

    func note(for lessonId: String) -> String {
        notes[lessonId] ?? ""
    }

    func toggleFavorite(_ lessonId: String) {
        if favorites.contains(lessonId) {
            favorites.remove(lessonId)
        } else {
            favorites.insert(lessonId)
        }
        UserDefaults.standard.set(Array(favorites), forKey: "hub.favorites")
    }

    func isFavorite(_ lessonId: String) -> Bool {
        favorites.contains(lessonId)
    }

    func setPosition(_ y: Double, for lessonId: String) {
        positions[lessonId] = y
        if positions.count > 400 {
            // 简单限制：超出就全量写一次
            if let d = try? JSONEncoder().encode(positions) {
                UserDefaults.standard.set(d, forKey: "hub.positions")
            }
            return
        }
        if let d = try? JSONEncoder().encode(positions) {
            UserDefaults.standard.set(d, forKey: "hub.positions")
        }
    }

    func position(for lessonId: String) -> Double {
        positions[lessonId] ?? 0
    }

    // MARK: 抽题与复习

    /// 到期待复习的条目（按到期时间排序）
    var dueReviews: [ReviewItem] {
        let now = Date()
        return reviews.values.filter { $0.due <= now }.sorted { $0.due < $1.due }
    }

    /// 艾宾浩斯间隔（天）
    private let reviewIntervals: [Double] = [1, 2, 4, 7, 15, 30]

    func recordReview(key: String, lessonId: String, lessonTitle: String, correct: Bool) {
        var it = reviews[key] ?? ReviewItem(key: key, box: 0, due: Date(),
                                            lessonId: lessonId, lessonTitle: lessonTitle)
        it.box = correct ? min(it.box + 1, reviewIntervals.count - 1) : 0
        it.due = Date().addingTimeInterval(reviewIntervals[it.box] * 86400)
        it.lessonId = lessonId
        it.lessonTitle = lessonTitle
        reviews[key] = it
        saveReviews()
    }

    /// 从所有章节里抽题。优先用已缓存的，缺的现拉。
    func pickQuestions(count: Int, chapters: [String]? = nil) async -> [QuizItem] {
        var pool: [QuizItem] = []
        let nodes = allLessonNodes.filter { n in
            guard let chapters else { return true }
            return chapters.contains { n.id.hasPrefix($0) }
        }
        for n in nodes {
            var lesson = cachedLesson(node: n)
            if lesson == nil {
                lesson = try? await loadLesson(node: n)
            }
            guard let lesson else { continue }
            for c in lesson.cards where c.type != "lecture" {
                pool.append(QuizItem(id: "\(lesson.id)|\(c.id)", lessonId: lesson.id,
                                     lessonTitle: lesson.title, card: c))
            }
        }
        guard !pool.isEmpty else { return [] }
        return Array(pool.shuffled().prefix(count))
    }

    /// 错题本 → 队列
    func wrongQuestions(limit: Int = 20) -> [QuizItem] {
        var out: [QuizItem] = []
        for w in wrongs.prefix(limit) {
            let node = Node(id: w.lessonId, title: w.lessonTitle, icon: nil, kind: "lesson",
                            summary: nil, children: nil, bundle: w.lessonId, badge: nil)
            if let lesson = cachedLesson(node: node),
               let card = lesson.cards.first(where: { $0.id == w.cardId }) {
                out.append(QuizItem(id: w.id, lessonId: w.lessonId,
                                    lessonTitle: w.lessonTitle, card: card))
            }
        }
        return out
    }

    /// 到期复习 → 队列
    func reviewQuestions(limit: Int = 30) async -> [QuizItem] {
        var out: [QuizItem] = []
        for r in dueReviews.prefix(limit) {
            let node = Node(id: r.lessonId, title: r.lessonTitle, icon: nil, kind: "lesson",
                            summary: nil, children: nil, bundle: r.lessonId, badge: nil)
            var lesson = cachedLesson(node: node)
            if lesson == nil { lesson = try? await loadLesson(node: node) }
            if let lesson, let card = lesson.cards.first(where: { $0.id == r.key.split(separator: "|").last.map(String.init) ?? "" }) {
                out.append(QuizItem(id: r.key, lessonId: r.lessonId,
                                    lessonTitle: r.lessonTitle, card: card))
            }
        }
        return out
    }

    /// 某章/某节的全部题（用于章节测验）
    func questions(in node: Node) async -> [QuizItem] {
        var out: [QuizItem] = []
        let list = node.kind == "folder" ? flatten(node.children ?? []) : [node]
        for n in list {
            var lesson = cachedLesson(node: n)
            if lesson == nil { lesson = try? await loadLesson(node: n) }
            guard let lesson else { continue }
            for c in lesson.cards where c.type != "lecture" {
                out.append(QuizItem(id: "\(lesson.id)|\(c.id)", lessonId: lesson.id,
                                    lessonTitle: lesson.title, card: c))
            }
        }
        return out
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

    func setTheme(_ t: String) {
        theme = t
        UserDefaults.standard.set(t, forKey: "hub.theme")
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

        // 主源失败自动切 GitHub 静态镜像
        let candidates = [client.baseURL, HubClient.mirrorBase]
        var succeeded = false
        var lastMsg = ""
        for base in candidates {
            client.activeBase = base
            do {
                let data = try await client.getRaw("/manifest")
                let m = try JSONDecoder().decode(Manifest.self, from: data)
                manifest = m
                client.saveCache(data, name: "manifest")
                let now = Date()
                lastSync = now
                UserDefaults.standard.set(now, forKey: "hub.lastSync")
                lastError = nil
                succeeded = true
                break
            } catch {
                lastMsg = error.localizedDescription
            }
        }
        if !succeeded {
            client.activeBase = client.baseURL
            lastError = lastMsg.isEmpty ? "内容源都连不上" : lastMsg
            return
        }
        await loadReplies()
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

        let path = client.lessonPath(key)
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
        scheduleCloudSync()

        // 艾宾浩斯排期
        recordReview(key: key, lessonId: lessonId, lessonTitle: lessonTitle, correct: correct)
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

    // MARK: - 账号与云同步

    @Published var username: String = ""
    @Published var loggedIn: Bool = false
    @Published var authBusy = false
    @Published var authError: String?
    @Published var registerOpen = false
    @Published var syncing = false
    @Published var syncMsg: String?

    /// 启动时恢复登录态并校验 token
    func refreshAuthState() async {
        let c = HubClient.shared
        if c.isLoggedIn {
            if let u = await c.me() {
                username = u
                loggedIn = true
                startPolling()
            } else {
                // token 失效
                c.userToken = ""
                c.username = ""
                loggedIn = false
                username = ""
            }
        } else {
            loggedIn = false
        }
        registerOpen = await c.registerOpen()
    }

    func doLogin(_ name: String, _ password: String) async -> Bool {
        authBusy = true; authError = nil
        defer { authBusy = false }
        do {
            let u = try await HubClient.shared.login(username: name, password: password)
            username = u
            loggedIn = true
            await syncDown(force: true)
            startPolling()
            return true
        } catch {
            authError = error.localizedDescription
            return false
        }
    }

    func doRegister(_ name: String, _ password: String) async -> Bool {
        authBusy = true; authError = nil
        defer { authBusy = false }
        do {
            let u = try await HubClient.shared.register(username: name, password: password)
            username = u
            loggedIn = true
            return true
        } catch {
            authError = error.localizedDescription
            return false
        }
    }

    func doLogout() async {
        stopPolling()
        await HubClient.shared.logout()
        loggedIn = false
        username = ""
        syncMsg = nil
    }

    /// 本地 → 云端
    func syncUp() async {
        guard loggedIn else { return }
        syncing = true; syncMsg = "上传中…"
        defer { syncing = false }
        var stats: [String: Int] = [:]
        stats["answered"] = progress.count
        stats["wrongs"] = wrongs.count
        stats["days"] = days.count
        let p = HubClient.ProgressPayload(progress: progress,
                                          wrongs: wrongs,
                                          notes: notes,
                                          stats: stats)
        do {
            try await HubClient.shared.pushProgress(p)
            let f = DateFormatter(); f.dateFormat = "HH:mm"
            syncMsg = "已同步 \(f.string(from: Date()))"
            lastSync = Date()
        } catch {
            syncMsg = "同步失败：\(error.localizedDescription)"
        }
    }

    private var lastPullAt: Date = .distantPast
    private var lastUpdated: Double = 0

    /// 云端 → 本地（登录后、回到前台、定时器都会调）
    func syncDown(force: Bool = false) async {
        guard loggedIn else { return }
        // 30 秒内不重复拉，避免频繁请求
        if !force, Date().timeIntervalSince(lastPullAt) < 30 { return }
        lastPullAt = Date()
        syncing = true; syncMsg = "拉取进度…"
        defer { syncing = false }
        do {
            let remote = try await HubClient.shared.pullProgress()
            if let rp = remote.progress, !rp.isEmpty {
                for (k, v) in rp {
                    let local = progress[k]
                    // 任一端答对就算对；本地没有才采信云端的 false
                    if v == true || local == nil { progress[k] = v }
                }
                saveProgress()
            }
            if let rn = remote.notes, !rn.isEmpty {
                for (k, v) in rn where notes[k] == nil { notes[k] = v }
                saveNotes()
            }
            if let rw = remote.wrongs {
                let have = Set(wrongs.map { $0.id })
                let add = rw.filter { !have.contains($0.id) }
                if !add.isEmpty {
                    wrongs.append(contentsOf: add)
                    saveWrongs()
                }
            }
            syncMsg = "进度已同步"
        } catch {
            syncMsg = "拉取失败：\(error.localizedDescription)"
        }
    }


    // MARK: - 自动同步（3 秒防抖）

    private var pendingSync: DispatchWorkItem?

    func scheduleCloudSync() {
        guard loggedIn else { return }
        pendingSync?.cancel()
        let work = DispatchWorkItem { [weak self] in
            guard let self else { return }
            Task { await self.syncUp() }
        }
        pendingSync = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 3, execute: work)
    }


    // MARK: - 长轮询（秒级一致）

    private var pollTask: Task<Void, Never>?

    /// 启动轮询循环：服务端挂 25 秒，有变化立即回；断线 3 秒后重连
    func startPolling() {
        guard loggedIn else { return }
        stopPolling()
        pollTask = Task { [weak self] in
            guard let self else { return }
            var since = self.lastUpdated
            while !Task.isCancelled {
                guard self.loggedIn else { break }
                do {
                    let (updated, payload) = try await HubClient.shared.pollProgress(since: since)
                    if updated > since { since = updated; self.lastUpdated = updated }
                    if let p = payload {
                        _ = self.applyRemote(p)
                    }
                } catch {
                    // 网络错误：退避 3 秒
                    try? await Task.sleep(nanoseconds: 3_000_000_000)
                }
            }
        }
    }

    func stopPolling() {
        pollTask?.cancel()
        pollTask = nil
    }

    /// 合并云端数据，返回是否有变化
    @discardableResult
    func applyRemote(_ p: HubClient.ProgressPayload) -> Bool {
        var changed = false
        if let rp = p.progress {
            for (k, v) in rp {
                let local = progress[k]
                if v == true || local == nil {
                    if progress[k] != v { changed = true }
                    progress[k] = v
                }
            }
        }
        if let rw = p.wrongs {
            let have = Set(wrongs.map { $0.id })
            let add = rw.filter { !have.contains($0.id) }
            if !add.isEmpty {
                wrongs.append(contentsOf: add)
                changed = true
            }
        }
        if changed {
            saveProgress()
            saveWrongs()
        }
        return changed
    }

}
