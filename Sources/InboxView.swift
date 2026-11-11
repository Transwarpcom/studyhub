import SwiftUI
import PhotosUI
import UniformTypeIdentifiers
import UIKit

struct InboxView: View {
    @EnvironmentObject var store: Store

    @State private var photoItem: PhotosPickerItem?
    @State private var note = ""
    @State private var busy = false
    @State private var toast: String?
    @State private var active: ActiveSheet?

    enum ActiveSheet: Identifiable {
        case camera
        case reply(Lesson)

        var id: String {
            switch self {
            case .camera: return "camera"
            case .reply(let l): return "reply-\(l.id)"
            }
        }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("有不会的，直接拍给我")
                            .font(.headline)
                        Text("拍照、相册、PDF、TXT 都行。传上来之后，讲解会出现在下面的「讲解回复」里，也会进课程树。")
                            .font(.footnote)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 4)
                }

                Section("发给我") {
                    TextField("说明（可选）：第几章、哪道题", text: $note, axis: .vertical)
                        .lineLimit(1...3)

                    PhotosPicker(selection: $photoItem, matching: .images) {
                        Label("从相册选图片", systemImage: "photo.on.rectangle.angled")
                    }

                    Button {
                        active = .camera
                    } label: {
                        Label("拍照", systemImage: "camera.fill")
                    }

                    Button {
                        chooseFile()
                    } label: {
                        Label("选 PDF / 文本文件", systemImage: "doc.fill")
                    }

                    if busy {
                        HStack(spacing: 8) {
                            ProgressView()
                            Text("上传中…").font(.footnote).foregroundColor(.secondary)
                        }
                    }
                }

                if let toast {
                    Section {
                        Text(toast)
                            .font(.footnote)
                            .foregroundColor(.secondary)
                    }
                }

                Section("我的提交") {
                    if store.uploads.isEmpty {
                        Text("还没有提交").foregroundColor(.secondary)
                    }
                    ForEach(store.uploads) { u in
                        HStack {
                            Image(systemName: "paperplane.fill")
                                .font(.caption)
                                .foregroundColor(.accentColor)
                            VStack(alignment: .leading, spacing: 1) {
                                Text(u.title).font(.subheadline).lineLimit(1)
                                Text(timeText(u.created)).font(.caption2).foregroundColor(.secondary)
                            }
                            Spacer()
                            Text(u.status)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Section("讲解回复") {
                    if store.replies.isEmpty {
                        Text("还没有回复").foregroundColor(.secondary)
                    }
                    ForEach(store.replies) { r in
                        Button {
                            active = .reply(r)
                        } label: {
                            HStack(spacing: 10) {
                                Image(systemName: "text.book.closed.fill")
                                    .foregroundColor(.accentColor)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(r.title).font(.subheadline).foregroundColor(.primary)
                                    if let s = r.subtitle, !s.isEmpty {
                                        Text(s).font(.caption).foregroundColor(.secondary).lineLimit(1)
                                    }
                                }
                                Spacer()
                                Text("\(r.cards.count) 张")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("答疑")
            .refreshable { await store.loadReplies() }
            .sheet(item: $active) { item in
                switch item {
                case .camera:
                    CameraPicker { img in
                        if let data = img.jpegData(compressionQuality: 0.82) {
                            upload(data, name: "photo-\(Int(Date().timeIntervalSince1970)).jpg", mime: "image/jpeg")
                        }
                    }
                    .ignoresSafeArea()
                case .reply(let lesson):
                    NavigationStack {
                        ReaderWebView(lesson: lesson)
                            .ignoresSafeArea(edges: .bottom)
                            .navigationTitle(lesson.title)
                            .navigationBarTitleDisplayMode(.inline)
                            .toolbar {
                                ToolbarItem(placement: .navigationBarTrailing) {
                                    Button("关闭") { active = nil }
                                }
                            }
                    }
                }
            }
            .onChange(of: photoItem) { newItem in
                guard let newItem else { return }
                Task {
                    if let data = try? await newItem.loadTransferable(type: Data.self) {
                        await MainActor.run {
                            upload(data, name: "photo-\(Int(Date().timeIntervalSince1970)).jpg", mime: "image/jpeg")
                        }
                    }
                    await MainActor.run { photoItem = nil }
                }
            }
        }
    }

    // MARK: - 行为

    private func chooseFile() {
        // fileImporter 挂在 NavigationStack 上不方便，简单起见用 UIDocumentPicker 包装
        let types: [UTType] = [.pdf, .image, .plainText, .data]
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: types, asCopy: true)
        let delegate = FileDelegate { url in
            let scoped = url.startAccessingSecurityScopedResource()
            defer { if scoped { url.stopAccessingSecurityScopedResource() } }
            if let data = try? Data(contentsOf: url) {
                let mime = UTType(filenameExtension: url.pathExtension)?.preferredMIMEType ?? "application/octet-stream"
                upload(data, name: url.lastPathComponent, mime: mime)
            } else {
                toast = "读不到这个文件"
            }
        }
        picker.delegate = delegate
        FileDelegate.keepAlive = delegate

        if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let root = scene.windows.first(where: { $0.isKeyWindow })?.rootViewController {
            var top = root
            while let p = top.presentedViewController { top = p }
            top.present(picker, animated: true)
        }
    }

    private func upload(_ data: Data, name: String, mime: String) {
        busy = true
        toast = nil
        let text = note
        Task {
            do {
                let id = try await store.upload(data: data, filename: name, mime: mime, note: text)
                await MainActor.run {
                    busy = false
                    note = ""
                    toast = "已提交（\(id)）。处理好后会出现在「讲解回复」里。"
                }
            } catch {
                await MainActor.run {
                    busy = false
                    toast = "上传失败：\(error.localizedDescription)"
                }
            }
        }
    }

    private func timeText(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "MM-dd HH:mm"
        return f.string(from: d)
    }
}

// MARK: - 文件选择回调

final class FileDelegate: NSObject, UIDocumentPickerDelegate {
    static var keepAlive: FileDelegate?
    private let onPick: (URL) -> Void

    init(onPick: @escaping (URL) -> Void) {
        self.onPick = onPick
    }

    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        if let u = urls.first { onPick(u) }
    }

    func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {}
}

// MARK: - 相机

struct CameraPicker: UIViewControllerRepresentable {
    var onImage: (UIImage) -> Void
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let p = UIImagePickerController()
        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            p.sourceType = .camera
        } else {
            p.sourceType = .photoLibrary
        }
        p.delegate = context.coordinator
        return p
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coord {
        Coord(self)
    }

    final class Coord: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraPicker

        init(_ parent: CameraPicker) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController,
                                   didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let img = info[.originalImage] as? UIImage {
                parent.onImage(img)
            }
            picker.dismiss(animated: true)
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            picker.dismiss(animated: true)
        }
    }
}
