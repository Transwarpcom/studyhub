import SwiftUI

// MARK: - 课程主页（文件夹树）

struct LibraryView: View {
    @EnvironmentObject var store: Store
    @State private var path: [Node] = []
    @State private var query = ""

    private var results: [Node] {
        let q = query.trimmingCharacters(in: .whitespaces)
        guard !q.isEmpty else { return [] }
        return store.allLessonNodes.filter {
            $0.title.localizedCaseInsensitiveContains(q) ||
            ($0.summary ?? "").localizedCaseInsensitiveContains(q)
        }
    }

    var body: some View {
        NavigationStack(path: $path) {
            List {
                if !query.isEmpty {
                    Section("搜索结果（\(results.count)）") {
                        if results.isEmpty {
                            Text("没有匹配的章节").foregroundColor(.secondary)
                        }
                        ForEach(results) { node in
                            NodeRow(node: node, path: $path)
                        }
                    }
                } else if let m = store.manifest {
                    Section {
                        OverviewCard(manifest: m)
                            .listRowInsets(EdgeInsets(top: 6, leading: 12, bottom: 6, trailing: 12))
                            .listRowBackground(Color.clear)
                    }
                    Section("课程") {
                        ForEach(m.tree) { node in
                            NodeRow(node: node, path: $path)
                                .swipeActions(edge: .trailing) {
                                    Button {
                                        Task { await store.download(node) }
                                    } label: {
                                        Label("缓存", systemImage: "arrow.down.circle")
                                    }
                                    .tint(.blue)
                                }
                        }
                    }
                    if let e = store.lastError {
                        Section {
                            Label(e, systemImage: "exclamationmark.triangle.fill")
                                .font(.footnote)
                                .foregroundColor(.orange)
                        }
                    }
                } else if store.loading {
                    Section {
                        HStack {
                            Spacer()
                            ProgressView("同步课程…")
                            Spacer()
                        }
                        .padding(.vertical, 30)
                    }
                } else {
                    Section {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("还没有内容").font(.headline)
                            Text(store.lastError ?? "连上网络后下拉刷新，或去「设置」检查服务器地址。")
                                .font(.footnote)
                                .foregroundColor(.secondary)
                            Button("重试") {
                                Task { await store.refresh() }
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        .padding(.vertical, 8)
                    }
                }
            }
            .listStyle(.insetGrouped)
            .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "搜索章节")
            .navigationTitle("学习台")
            .refreshable { await store.refresh() }
            .navigationDestination(for: Node.self) { node in
                if node.kind == "folder" {
                    FolderView(node: node, path: $path)
                } else {
                    LessonLoaderView(node: node)
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        Task { await store.refresh() }
                    } label: {
                        Image(systemName: "arrow.triangle.2.circlepath")
                    }
                }
            }
        }
    }
}

// MARK: - 文件夹页

struct FolderView: View {
    let node: Node
    @Binding var path: [Node]
    @EnvironmentObject var store: Store

    var body: some View {
        List {
            if let s = node.summary, !s.isEmpty {
                Section {
                    Text(s)
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
            }
            Section {
                let kids = node.children ?? []
                if kids.isEmpty {
                    Text("这一层还是空的").foregroundColor(.secondary)
                }
                ForEach(kids) { child in
                    NodeRow(node: child, path: $path)
                        .swipeActions(edge: .trailing) {
                            Button {
                                Task { await store.download(child) }
                            } label: {
                                Label("缓存", systemImage: "arrow.down.circle")
                            }
                            .tint(.blue)
                        }
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle(node.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - 一行节点

struct NodeRow: View {
    let node: Node
    @Binding var path: [Node]

    private var isFolder: Bool { node.kind == "folder" }

    private var iconName: String {
        if let i = node.icon, !i.isEmpty { return i }
        return isFolder ? "folder.fill" : "doc.text.fill"
    }

    var body: some View {
        Button {
            path.append(node)
        } label: {
            HStack(spacing: 12) {
                Image(systemName: iconName)
                    .font(.system(size: 17, weight: .medium))
                    .foregroundColor(isFolder ? .accentColor : .secondary)
                    .frame(width: 26, alignment: .center)

                VStack(alignment: .leading, spacing: 2) {
                    Text(node.title)
                        .font(.body)
                        .foregroundColor(.primary)
                        .multilineTextAlignment(.leading)
                    if let s = node.summary, !s.isEmpty {
                        Text(s)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }
                }

                Spacer(minLength: 6)

                if let b = node.badge, !b.isEmpty {
                    Text(b)
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Capsule().fill(Color.accentColor.opacity(0.12)))
                        .foregroundColor(.accentColor)
                }

                if isFolder {
                    Text("\(node.children?.count ?? 0)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(Color.secondary.opacity(0.45))
            }
            .padding(.vertical, 3)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

// MARK: - 顶部概览

struct OverviewCard: View {
    let manifest: Manifest
    @EnvironmentObject var store: Store

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 3) {
                    Text(manifest.title ?? "学习台")
                        .font(.title3.bold())
                    Text("内容版本 v\(manifest.version)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                Image(systemName: "graduationcap.fill")
                    .font(.system(size: 26))
                    .foregroundColor(.accentColor)
            }

            let answered = store.progress.count
            let right = store.progress.values.filter { $0 }.count
            HStack(spacing: 18) {
                stat("已答", "\(answered)")
                stat("答对", "\(right)")
                stat("正确率", answered > 0 ? "\(right * 100 / answered)%" : "—")
                Spacer()
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(uiColor: .secondarySystemGroupedBackground))
        )
    }

    private func stat(_ title: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(value)
                .font(.system(.headline, design: .rounded))
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - 章节加载

struct LessonLoaderView: View {
    let node: Node
    @EnvironmentObject var store: Store
    @State private var lesson: Lesson?
    @State private var error: String?

    var body: some View {
        Group {
            if let lesson {
                ReaderWebView(lesson: lesson)
                    .ignoresSafeArea(edges: .bottom)
            } else if let error {
                VStack(spacing: 14) {
                    Image(systemName: "wifi.exclamationmark")
                        .font(.system(size: 34))
                        .foregroundColor(.orange)
                    Text(error)
                        .font(.footnote)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 30)
                    Button("重试") { Task { await load(force: true) } }
                        .buttonStyle(.borderedProminent)
                }
            } else {
                ProgressView("加载这一节…")
            }
        }
        .navigationTitle(node.title)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            if lesson == nil { await load(force: false) }
        }
    }

    private func load(force: Bool) async {
        error = nil
        if !force, let cached = store.cachedLesson(node: node) {
            lesson = cached
            return
        }
        do {
            lesson = try await store.loadLesson(node: node)
        } catch {
            self.error = error.localizedDescription
        }
    }
}
