import Foundation

// 本地默认配置。CI 构建时会用 GitHub Secret 覆盖这个文件，
// 服务器地址可在这里改，用户也能在设置里覆盖。
enum BuildConfig {
    // 已备案域名 + Let's Encrypt 正式证书，iOS 无需安装任何根证书
    static let defaultBaseURL = "https://study.medwarp.com.cn"
}
