import Foundation

// MARK: - 轻量日志（只存最近 300 条，设置页可导出）

enum Log {
    private static let key = "hub.log"
    private static let lock = NSLock()

    static func add(_ msg: String) {
        let f = DateFormatter()
        f.dateFormat = "MM-dd HH:mm:ss"
        let line = "[\(f.string(from: Date()))] \(msg)"
        lock.lock()
        var arr = UserDefaults.standard.stringArray(forKey: key) ?? []
        arr.append(line)
        if arr.count > 300 { arr = Array(arr.suffix(300)) }
        UserDefaults.standard.set(arr, forKey: key)
        lock.unlock()
    }

    static var lines: [String] {
        UserDefaults.standard.stringArray(forKey: key) ?? []
    }

    static var text: String {
        let l = lines
        return l.isEmpty ? "（还没有日志）" : l.joined(separator: "\n")
    }

    static func clear() {
        UserDefaults.standard.removeObject(forKey: key)
    }
}

// MARK: - Widget 共享数据

enum Shared {
    static let suite = "group.cn.medwarp.studyhub"

    static var defaults: UserDefaults {
        UserDefaults(suiteName: suite) ?? .standard
    }

    static func publish(due: Int, today: Int, wrong: Int, streak: Int) {
        let d = defaults
        d.set(due, forKey: "widget.due")
        d.set(today, forKey: "widget.today")
        d.set(wrong, forKey: "widget.wrong")
        d.set(streak, forKey: "widget.streak")
    }
}
