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
            if code == 401 { return "口令不对（401），去设置里改访问口令" }
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
        get { defaults.string(forKey: "hub.baseURL") ?? "https://html.medwarp.cn/study-api" }
        set { defaults.set(newValue, forKey: "hub.baseURL") }
    }

    var token: String {
        get { defaults.string(forKey: "hub.token") ?? "" }
        set { defaults.set(newValue, forKey: "hub.token") }
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
        let base = baseURL.trimmingCharacters(in: .whitespacesAndNewlines)
        guard var comps = URLComponents(string: base + path) else { throw HubError.badURL }
        if comps.scheme == nil { comps.scheme = "https" }
        guard let url = comps.url else { throw HubError.badURL }
        var r = URLRequest(url: url)
        r.httpMethod = method
        r.timeoutInterval = 30
        r.setValue("application/json", forHTTPHeaderField: "Accept")
        let t = token.trimmingCharacters(in: .whitespacesAndNewlines)
        if !t.isEmpty {
            r.setValue("Bearer \(t)", forHTTPHeaderField: "Authorization")
        } else {
            r.setValue("Bearer public", forHTTPHeaderField: "Authorization")
        }
        return r
    }

    func get<T: Decodable>(_ path: String, as type: T.Type) async throws -> T {
        let req = try makeRequest(path)
        let (data, resp) = try await URLSession.shared.data(for: req)
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
        let (data, resp) = try await URLSession.shared.data(for: req)
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

        let (respData, resp) = try await URLSession.shared.data(for: req)
        if let h = resp as? HTTPURLResponse, h.statusCode != 200 {
            let b = String(data: Data(respData.prefix(300)), encoding: .utf8) ?? ""
            throw HubError.http(h.statusCode, b)
        }
        return (try? JSONDecoder().decode(UploadResp.self, from: respData))
            ?? UploadResp(ok: false, id: nil, error: "返回格式不对")
    }
}
