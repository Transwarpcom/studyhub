import Foundation

// 本地默认配置。CI 构建时会用 GitHub Secret 覆盖这个文件，
// 服务器地址可在这里改，用户也能在设置里覆盖。
enum BuildConfig {
    static let defaultBaseURL = "https://47.104.168.254:8443"
}
