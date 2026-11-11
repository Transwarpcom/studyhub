import Foundation

// 本地默认配置。CI 构建时会用 GitHub Secret 覆盖这个文件，
// 因此真实访问口令不会出现在仓库里。
enum BuildConfig {
    static let defaultBaseURL = "https://us.medwarp.cn/study-api"
    static let defaultToken = ""
}
