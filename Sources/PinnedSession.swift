import Foundation
import CryptoKit

/// 证书固定（certificate pinning）
/// 只认服务端那一张自签证书的 SHA-256，不依赖系统信任链，
/// 因此不需要把自签 CA 装进设备，也不受「完全信任」开关限制。
final class PinnedSession: NSObject, URLSessionDelegate {

    static let shared = PinnedSession()

    /// 允许的叶子证书 SHA-256（小写十六进制）
    /// 换证书时改这里。留空表示不校验（仅用于本地调试）。
    static var pins: Set<String> = ["21f7c8d2e607c5fa722460e6adeac216464cc6775597e51f51e1d532a3c3506b"]

    /// 只对指定主机启用 pinning，其余走系统默认
    static var pinnedHosts: Set<String> = ["47.104.168.254"]

    lazy var session: URLSession = {
        let cfg = URLSessionConfiguration.default
        cfg.timeoutIntervalForRequest = 25
        cfg.timeoutIntervalForResource = 120
        cfg.waitsForConnectivity = false
        return URLSession(configuration: cfg, delegate: self, delegateQueue: nil)
    }()

    // MARK: URLSessionDelegate

    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {

        let space = challenge.protectionSpace
        guard space.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              Self.pinnedHosts.contains(space.host),
              let trust = space.serverTrust else {
            completionHandler(.performDefaultHandling, nil)
            return
        }

        guard !Self.pins.isEmpty else {
            completionHandler(.performDefaultHandling, nil)
            return
        }

        // 取叶子证书算 SHA-256
        guard let chain = SecTrustCopyCertificateChain(trust) as? [SecCertificate],
              let leaf = chain.first else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        let der = SecCertificateCopyData(leaf) as Data
        let digest = SHA256.hash(data: der)
        let hex = digest.map { String(format: "%02x", $0) }.joined()

        if Self.pins.contains(hex) {
            completionHandler(.useCredential, URLCredential(trust: trust))
        } else {
            #if DEBUG
            print("[pin] 证书不匹配: \(hex)")
            #endif
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
