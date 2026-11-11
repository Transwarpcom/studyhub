import Foundation

// MARK: - 课程树

struct Manifest: Codable {
    var version: Int
    var updated: String?
    var title: String?
    var tree: [Node]
}

struct Node: Codable, Identifiable, Hashable {
    var id: String
    var title: String
    var icon: String?
    var kind: String          // folder | lesson
    var summary: String?
    var children: [Node]?
    var bundle: String?
    var badge: String?
}

// MARK: - 章节与卡片

struct Lesson: Codable, Identifiable, Hashable {
    var id: String
    var title: String
    var subtitle: String?
    var cards: [Card]
}

struct Card: Codable, Identifiable, Hashable {
    var id: String
    var type: String          // lecture | choice | judge | blank | text
    var title: String?
    var md: String?           // lecture 正文（Markdown + $公式$ + ```svg 块）
    var question: String?     // 题干
    var options: [String]?
    var answer: [Int]?        // 正确选项下标（多选为多个）
    var blanks: [[String]]?   // 每个空的可接受答案
    var explain: String?
    var tags: [String]?
    var svg: String?
}

struct ReplyList: Codable {
    var version: Int?
    var replies: [Lesson]
}

struct UploadResp: Codable {
    var ok: Bool
    var id: String?
    var error: String?
}

// MARK: - 本地记录

struct UploadRecord: Codable, Identifiable {
    var id: String
    var title: String
    var created: Date
    var status: String
}
