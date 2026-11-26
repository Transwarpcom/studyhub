import Foundation

/// 一章的掌握情况
struct ChapterStat: Identifiable, Hashable {
    var id: String
    var title: String
    var total: Int
    var answered: Int
    var correct: Int
    var due: Int
    var wrong: Int

    var progress: Double {
        total > 0 ? Double(answered) / Double(total) : 0
    }
    var accuracy: Double {
        answered > 0 ? Double(correct) / Double(answered) : 0
    }
}
