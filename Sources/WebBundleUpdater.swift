import Foundation
import CryptoKit

/// App 内嵌网页资源（reader.html / reader.js / katex）的热更新。
///
/// 策略：
///   1. 启动时直接用包内资源，绝不阻塞界面
///   2. 后台向服务端要清单（每个文件的 sha256 + size）
///   3. 逐项比对，只下载变化的文件到临时目录
///   4. 全部下载完再逐个校验 sha256，任一不符就整批放弃
///   5. 校验通过后原子替换 Document/webhot 目录，并写版本标记
///   6. 下次启动优先从 webhot 加载；失败自动回退到包内资源
final class WebBundleUpdater {

    static let shared = WebBundleUpdater()

    private let fm = FileManager.default
    private let versionKey = "hub.webbundle.version"
    private let fallbackKey = "hub.webbundle.failed"

    /// 热更新目录（Documents/webhot），可写
    var hotDir: URL {
        fm.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("webhot", isDirectory: true)
    }

    /// 包内原始资源目录（只读）
    var bundledDir: URL? {
        Bundle.main.url(forResource: "web", withExtension: nil)
    }

    /// 当前应该加载的 reader.html
    func activeReaderURL() -> URL? {
        let hot = hotDir.appendingPathComponent("reader.html")
        if fm.fileExists(atPath: hot.path) {
            return hot
        }
        return bundledDir?.appendingPathComponent("reader.html")
    }

    // MARK: - 检查更新

    /// 静默检查并更新。完成后回调是否发生了变化。
    func checkAndUpdate(baseURL: String, token: String, completion: ((Bool) -> Void)? = nil) {
        guard let manifestURL = URL(string: baseURL + "/appbundle/manifest.json") else {
            completion?(false); return
        }

        var req = URLRequest(url: manifestURL)
        req.timeoutInterval = 20
        req.setValue("application/json", forHTTPHeaderField: "Accept")
        if !token.isEmpty {
            req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        PinnedSession.shared.session.dataTask(with: req) { [weak self] data, resp, err in
            guard let self,
                  err == nil,
                  let data,
                  (resp as? HTTPURLResponse)?.statusCode == 200,
                  let manifest = try? JSONDecoder().decode(Manifest.self, from: data)
            else {
                completion?(false); return
            }

            // 版本没变就不动
            let current = UserDefaults.standard.string(forKey: self.versionKey) ?? ""
            if manifest.version == current {
                completion?(false); return
            }

            self.download(manifest: manifest, baseURL: baseURL, token: token, completion: completion)
        }.resume()
    }

    // MARK: - 下载

    struct Manifest: Codable {
        let ok: Bool?
        let version: String
        let count: Int
        let files: [FileEntry]

        struct FileEntry: Codable {
            let path: String
            let sha256: String
            let size: Int
        }
    }

    private func download(manifest: Manifest, baseURL: String, token: String,
                          completion: ((Bool) -> Void)?) {
        let staging = fm.temporaryDirectory
            .appendingPathComponent("webstage-\(UUID().uuidString.prefix(8))", isDirectory: true)
        try? fm.createDirectory(at: staging, withIntermediateDirectories: true)

        let group = DispatchGroup()
        let lock = NSLock()
        var failed = false
        var verified: [String: String] = [:]   // path -> sha256

        for entry in manifest.files {
            group.enter()
            guard let url = URL(string: baseURL + "/appbundle/" + entry.path) else {
                failed = true; group.leave(); continue
            }
            var req = URLRequest(url: url)
            req.timeoutInterval = 60
            if !token.isEmpty {
                req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }

            PinnedSession.shared.session.downloadTask(with: req) { [weak self] tmp, resp, err in
                defer { group.leave() }
                guard let self else { return }

                guard err == nil,
                      let tmp,
                      (resp as? HTTPURLResponse)?.statusCode == 200
                else {
                    lock.lock(); failed = true; lock.unlock()
                    return
                }

                guard let data = try? Data(contentsOf: tmp) else {
                    lock.lock(); failed = true; lock.unlock()
                    return
                }

                // 大小先比，快速失败
                if data.count != entry.size {
                    lock.lock(); failed = true; lock.unlock()
                    return
                }

                // sha256 校验
                let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
                if digest != entry.sha256 {
                    lock.lock(); failed = true; lock.unlock()
                    return
                }

                let dest = staging.appendingPathComponent(entry.path)
                do {
                    try self.fm.createDirectory(at: dest.deletingLastPathComponent(),
                                           withIntermediateDirectories: true)
                    try data.write(to: dest)
                    lock.lock(); verified[entry.path] = digest; lock.unlock()
                } catch {
                    lock.lock(); failed = true; lock.unlock()
                }
            }.resume()
        }

        group.notify(queue: .global(qos: .utility)) { [weak self] in
            guard let self else { return }

            if failed || verified.count != manifest.files.count {
                try? self.fm.removeItem(at: staging)
                UserDefaults.standard.set(manifest.version, forKey: self.fallbackKey)
                print("[webbundle] 下载校验失败，保持本地版本")
                completion?(false)
                return
            }

            // 关键文件必须在
            let need = ["reader.html", "reader.js"]
            for n in need where !self.fm.fileExists(atPath: staging.appendingPathComponent(n).path) {
                try? self.fm.removeItem(at: staging)
                print("[webbundle] 缺少 \(n)，放弃")
                completion?(false)
                return
            }

            self.swap(staging: staging, version: manifest.version, completion: completion)
        }
    }

    /// 原子替换：旧目录改名备份 → 新目录就位 → 删备份
    private func swap(staging: URL, version: String, completion: ((Bool) -> Void)?) {
        let target = hotDir
        let backup = target.deletingLastPathComponent()
            .appendingPathComponent("webhot.old", isDirectory: true)

        do {
            try? fm.removeItem(at: backup)

            if fm.fileExists(atPath: target.path) {
                try fm.moveItem(at: target, to: backup)
            }

            try fm.moveItem(at: staging, to: target)

            // 复核
            let reader = target.appendingPathComponent("reader.html")
            guard fm.fileExists(atPath: reader.path) else {
                throw NSError(domain: "webbundle", code: 1,
                              userInfo: [NSLocalizedDescriptionKey: "替换后缺少 reader.html"])
            }

            try? fm.removeItem(at: backup)
            UserDefaults.standard.set(version, forKey: versionKey)
            UserDefaults.standard.removeObject(forKey: fallbackKey)
            print("[webbundle] 已更新到 \(version)")
            completion?(true)

        } catch {
            // 回滚
            try? fm.removeItem(at: target)
            if fm.fileExists(atPath: backup.path) {
                try? fm.moveItem(at: backup, to: target)
            }
            print("[webbundle] 替换失败，已回滚：\(error.localizedDescription)")
            completion?(false)
        }
    }

    /// 清掉热更新，回到包内版本
    func reset() {
        try? fm.removeItem(at: hotDir)
        UserDefaults.standard.removeObject(forKey: versionKey)
    }

    /// 当前生效的版本（包内 or 热更新）
    func currentVersionInfo() -> String {
        let v = UserDefaults.standard.string(forKey: versionKey)
        if let v, fm.fileExists(atPath: hotDir.appendingPathComponent("reader.html").path) {
            return "热更新 " + v
        }
        let bv = (Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String) ?? "?"
        return "内置 " + bv
    }
}
