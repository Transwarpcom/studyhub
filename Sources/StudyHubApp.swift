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
    @Environment(\.scenePhase) private var scenePhase
    @State private var tab = 0

    var body: some View {
        TabView(selection: $tab) {
            TodayView()
                .tabItem { Label("今日", systemImage: "sun.max.fill") }
                .tag(0)
            LibraryView()
                .tabItem { Label("课程", systemImage: "books.vertical.fill") }
                .tag(1)
            InboxView()
                .tabItem { Label("答疑", systemImage: "tray.full.fill") }
                .tag(2)
            SettingsView()
                .tabItem { Label("设置", systemImage: "gearshape.fill") }
                .tag(3)
        }
        .task {
            HubClient.migrateServerAddressIfNeeded()
            StoreLocator.shared.store = store
            await store.bootstrap()
            await store.refreshAuthState()
            // 后台检查 App 内嵌资源有没有新版（不阻塞界面）
            WebBundleUpdater.shared.checkAndUpdate(baseURL: HubClient.shared.baseURL,
                                                   token: HubClient.shared.userToken) { _ in }
        }
        .onChange(of: scenePhase) { phase in
            // 回到前台：自动拉一次云端进度（别的设备可能改过）
            guard phase == .active, store.loggedIn else { return }
            Task { await store.syncDown() }
        }
    }
}
