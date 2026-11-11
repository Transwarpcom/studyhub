import SwiftUI

@main
struct StudyHubApp: App {
    @StateObject private var store = Store()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
        }
    }
}

struct RootView: View {
    @EnvironmentObject var store: Store
    @State private var tab = 0

    var body: some View {
        TabView(selection: $tab) {
            LibraryView()
                .tabItem { Label("课程", systemImage: "books.vertical.fill") }
                .tag(0)
            InboxView()
                .tabItem { Label("答疑", systemImage: "tray.full.fill") }
                .tag(1)
            SettingsView()
                .tabItem { Label("设置", systemImage: "gearshape.fill") }
                .tag(2)
        }
        .task {
            StoreLocator.shared.store = store
            await store.bootstrap()
        }
    }
}
