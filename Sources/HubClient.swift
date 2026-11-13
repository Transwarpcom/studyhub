import Foundation

enum HubError: LocalizedError {
    case badURL
    case http(Int, String)
    case decode(String)

    var errorDescription: String? {
        switch self {
        case .badURL:
            return "服务器地址无效，去设置里检查一下"
        case .http(let code, let body):
            if code == 401 { return "登录已失效（401），请重新登录" }
            return "服务器返回 \(code) \(body)"
        case .decode(let msg):
            return "数据解析失败：\(msg)"
        }
    }
}

final class HubClient {
    static let shared = HubClient()
    private let defaults = UserDefaults.standard

    var baseURL: String {
        get { defaults.string(forKey: "hub.baseURL") ?? BuildConfig.defaultBaseURL }
        set { defaults.set(newValue, forKey: "hub.baseURL") }
    }

    /// 一次性迁移：把历史版本留下的服务器地址清掉，改用 BuildConfig 的新默认值，
    /// 否则旧地址会一直覆盖默认值（表现为登录 404 no route）。
    static func migrateServerAddressIfNeeded() {
        let key = "hub.baseURL"
        let d = UserDefaults.standard
        guard let cur = d.string(forKey: key), !cur.isEmpty else { return }
        let legacy = [
            "https://html.medwarp.cn/study-api",
            "https://us.medwarp.cn/study-api",
            "https://html.medwarp.cn",
            "https://us.medwarp.cn",
            "http://47.104.168.254:8099",
            "http://47.104.168.254",
        ]
        if legacy.contains(where: { cur.hasPrefix($0) }) {
            d.removeObject(forKey: key)
            d.removeObject(forKey: "hub.activeBase")
            print("[migrate] 旧服务器地址已清除：\(cur) → \(BuildConfig.defaultBaseURL)")
        }
    }

    // MARK: 内容源（主服务器失效时自动切 GitHub 静态镜像）

    /// GitHub 上的静态镜像（content 目录直接跑 raw）
    static let mirrorBase = "https://raw.githubusercontent.com/Transwarpcom/studyhub/main/content"

    /// 当前实际使用的源
    var activeBase: String {
        get { defaults.string(forKey: "hub.activeBase") ?? baseURL }
        set { defaults.set(newValue, forKey: "hub.activeBase") }
    }

    var isStatic: Bool {
        activeBase.contains("raw.githubusercontent.com")
    }

    /// 静态镜像的章节路径：/lessons/<id 下划线化>.json
    func lessonPath(_ key: String) -> String {
        if isStatic {
            return "/lessons/" + key.replacingOccurrences(of: "/", with: "_") + ".json"
        }
        let enc = key.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? key
        return "/lesson?id=" + enc
    }

    // MARK: 缓存

    var cacheDir: URL {
        let d = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("studyhub", isDirectory: true)
        if !FileManager.default.fileExists(atPath: d.path) {
            try? FileManager.default.createDirectory(at: d, withIntermediateDirectories: true)
        }
        return d
    }

    func cacheURL(_ name: String) -> URL {
        let safe = name.replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: ":", with: "_")
        return cacheDir.appendingPathComponent(safe + ".json")
    }

    func saveCache(_ data: Data, name: String) {
        try? data.write(to: cacheURL(name), options: .atomic)
    }

    func loadCache(name: String) -> Data? {
        try? Data(contentsOf: cacheURL(name))
    }

    func clearCache() {
        let fm = FileManager.default
        if let items = try? fm.contentsOfDirectory(at: cacheDir, includingPropertiesForKeys: nil) {
            for it in items { try? fm.removeItem(at: it) }
        }
    }

    // MARK: 请求

    private func makeRequest(_ path: String, method: String = "GET") throws -> URLRequest {
        let base = activeBase.trimmingCharacters(in: .whitespacesAndNewlines)
        guard var comps = URLComponents(string: base + path) else { throw HubError.badURL }
        if comps.scheme == nil { comps.scheme = "https" }
        guard let url = comps.url else { throw HubError.badURL }
        var r = URLRequest(url: url)
        r.httpMethod = method
        r.timeoutInterval = 30
        r.setValue("application/json", forHTTPHeaderField: "Accept")
        // 课程内容公开，无需口令；登录后带上用户 token 便于服务端识别
        let t = userToken.trimmingCharacters(in: .whitespacesAndNewlines)
        if !t.isEmpty {
            r.setValue("Bearer \(t)", forHTTPHeaderField: "Authorization")
        }
        return r
    }

    func get<T: Decodable>(_ path: String, as type: T.Type) async throws -> T {
        let req = try makeRequest(path)
        let (data, resp) = try await PinnedSession.shared.session.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode != 200 {
            let body = String(data: Data(data.prefix(300)), encoding: .utf8) ?? ""
            throw HubError.http(h.statusCode, body)
        }
        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw HubError.decode(String(describing: error))
        }
    }

    func getRaw(_ path: String) async throws -> Data {
        let req = try makeRequest(path)
        let (data, resp) = try await PinnedSession.shared.session.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode != 200 {
            let body = String(data: Data(data.prefix(300)), encoding: .utf8) ?? ""
            throw HubError.http(h.statusCode, body)
        }
        return data
    }

    // MARK: 上传

    func upload(data: Data, filename: String, mime: String, note: String) async throws -> UploadResp {
        var req = try makeRequest("/upload", method: "POST")
        let boundary = "----StudyHub" + UUID().uuidString.replacingOccurrences(of: "-", with: "")
        var body = Data()

        func add(_ s: String) {
            if let d = s.data(using: .utf8) { body.append(d) }
        }

        add("--\(boundary)\r\n")
        add("Content-Disposition: form-data; name=\"note\"\r\n\r\n")
        add(note + "\r\n")
        add("--\(boundary)\r\n")
        add("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n")
        add("Content-Type: \(mime)\r\n\r\n")
        body.append(data)
        add("\r\n--\(boundary)--\r\n")

        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        req.httpBody = body

        let (respData, resp) = try await PinnedSession.shared.session.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode != 200 {
            let b = String(data: Data(respData.prefix(300)), encoding: .utf8) ?? ""
            throw HubError.http(h.statusCode, b)
        }
        return (try? JSONDecoder().decode(UploadResp.self, from: respData))
            ?? UploadResp(ok: false, id: nil, error: "返回格式不对")
    }

    // MARK: - 账号

    /// 用户 token（与旧的 reader token 分开存）
    var userToken: String {
        get { defaults.string(forKey: "hub.userToken") ?? "" }
        set { defaults.set(newValue, forKey: "hub.userToken") }
    }

    var username: String {
        get { defaults.string(forKey: "hub.username") ?? "" }
        set { defaults.set(newValue, forKey: "hub.username") }
    }

    var isLoggedIn: Bool { !userToken.isEmpty }

    struct AuthResp: Decodable {
        let ok: Bool?
        let token: String?
        let username: String?
        let error: String?
        let message: String?
    }

    struct MeResp: Decodable {
        let ok: Bool?
        let username: String?
        let registerOpen: Bool?
        let error: String?
    }

    private func postJSON(_ path: String, _ payload: [String: Any], auth: Bool) async throws -> Data {
        guard let u = URL(string: baseURL + path) else { throw HubError.badURL }
        var req = URLRequest(url: u)
        req.httpMethod = "POST"
        req.timeoutInterval = 20
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if auth && !userToken.isEmpty {
            req.setValue("Bearer \(userToken)", forHTTPHeaderField: "Authorization")
        }
        req.httpBody = try JSONSerialization.data(withJSONObject: payload)
        let (data, resp) = try await PinnedSession.shared.session.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode >= 400 {
            let text = String(data: Data(data.prefix(400)), encoding: .utf8) ?? ""
            if let d = try? JSONDecoder().decode(AuthResp.self, from: data),
               let m = d.message ?? d.error {
                throw HubError.http(h.statusCode, m)
            }
            throw HubError.http(h.statusCode, text)
        }
        return data
    }

    @discardableResult
    func login(username name: String, password: String) async throws -> String {
        let data = try await postJSON("/auth/login", ["username": name, "password": password], auth: false)
        let d = try JSONDecoder().decode(AuthResp.self, from: data)
        guard let t = d.token, !t.isEmpty else {
            throw HubError.decode(d.error ?? "登录失败")
        }
        userToken = t
        username = d.username ?? name
        return username
    }

    @discardableResult
    func register(username name: String, password: String) async throws -> String {
        let data = try await postJSON("/auth/register", ["username": name, "password": password], auth: false)
        let d = try JSONDecoder().decode(AuthResp.self, from: data)
        guard let t = d.token, !t.isEmpty else {
            throw HubError.decode(d.error ?? "注册失败")
        }
        userToken = t
        username = d.username ?? name
        return username
    }

    /// 服务端注册开关
    func registerOpen() async -> Bool {
        guard let u = URL(string: baseURL + "/auth/config") else { return false }
        var req = URLRequest(url: u)
        req.timeoutInterval = 12
        guard let (data, _) = try? await PinnedSession.shared.session.data(for: req),
              let d = try? JSONDecoder().decode(MeResp.self, from: data) else { return false }
        return d.registerOpen ?? false
    }

    /// 校验 token 是否还有效
    func me() async -> String? {
        guard !userToken.isEmpty, let u = URL(string: baseURL + "/auth/me") else { return nil }
        var req = URLRequest(url: u)
        req.timeoutInterval = 12
        req.setValue("Bearer \(userToken)", forHTTPHeaderField: "Authorization")
        guard let (data, resp) = try? await PinnedSession.shared.session.data(for: req),
              (resp as? HTTPURLResponse)?.statusCode == 200,
              let d = try? JSONDecoder().decode(MeResp.self, from: data) else { return nil }
        return d.username
    }

    func logout() async {
        _ = try? await postJSON("/auth/logout", [:], auth: true)
        userToken = ""
        username = ""
    }

    // MARK: - 进度

    struct ProgressPayload: Codable {
        var progress: [String: Bool]?
        var wrongs: [WrongItem]?
        var notes: [String: String]?
        var stats: [String: Int]?
    }

    struct ProgressResp: Codable {
        let ok: Bool?
        let username: String?
        let data: ProgressPayload?
    }

    func pullProgress() async throws -> ProgressPayload {
        guard let u = URL(string: baseURL + "/progress") else { throw HubError.badURL }
        var req = URLRequest(url: u)
        req.timeoutInterval = 20
        req.setValue("Bearer \(userToken)", forHTTPHeaderField: "Authorization")
        let (data, resp) = try await PinnedSession.shared.session.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode != 200 {
            throw HubError.http(h.statusCode, String(data: Data(data.prefix(200)), encoding: .utf8) ?? "")
        }
        let d = try JSONDecoder().decode(ProgressResp.self, from: data)
        return d.data ?? ProgressPayload()
    }

    struct PollResp: Codable {
        let ok: Bool?
        let username: String?
        let updated: Double?
        let data: ProgressPayload?
    }

    /// 长轮询：服务端最多挂 25 秒，有变化立刻返回
    func pollProgress(since: Double) async throws -> (updated: Double, payload: ProgressPayload?) {
        guard let u = URL(string: baseURL + "/progress/poll?since=\(since)") else { throw HubError.badURL }
        var req = URLRequest(url: u)
        req.timeoutInterval = 40
        req.setValue("Bearer \(userToken)", forHTTPHeaderField: "Authorization")
        let (data, resp) = try await PinnedSession.shared.session.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode != 200 {
            throw HubError.http(h.statusCode, String(data: Data(data.prefix(200)), encoding: .utf8) ?? "")
        }
        let d = try JSONDecoder().decode(PollResp.self, from: data)
        return (d.updated ?? since, d.data)
    }

    func pushProgress(_ p: ProgressPayload) async throws {
        var body: [String: Any] = [:]
        if let x = p.progress { body["progress"] = x }
        if let x = p.notes { body["notes"] = x }
        if let x = p.stats { body["stats"] = x }
        if let x = p.wrongs {
            body["wrongs"] = x.map { w -> [String: Any] in
                ["id": w.id, "lessonId": w.lessonId, "lessonTitle": w.lessonTitle,
                 "cardId": w.cardId, "preview": w.preview,
                 "ts": ISO8601DateFormatter().string(from: w.ts)]
            }
        }
        _ = try await postJSON("/progress", body, auth: true)
    }

}
