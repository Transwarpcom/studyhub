import SwiftUI

/// 账号：登录后进度随账号走，课程与题目所有人可见
struct AccountView: View {
    @EnvironmentObject var store: Store
    @Environment(\.dismiss) private var dismiss

    @State private var user = ""
    @State private var pass = ""
    @State private var showPass = false
    @State private var showRegister = false
    @State private var regUser = ""
    @State private var regPass = ""
    @State private var regPass2 = ""
    @State private var toast: String?

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 14) {
                    header
                    if store.loggedIn { loggedInCards } else { loginCard }
                    footNote
                }
                .padding(16)
            }
            .background(Color(.systemGroupedBackground).ignoresSafeArea())
            .navigationTitle("账号")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("关闭") { dismiss() }
                }
            }
            .task { await store.refreshAuthState() }
            .alert("提示", isPresented: Binding(get: { toast != nil }, set: { if !$0 { toast = nil } })) {
                Button("好") { toast = nil }
            } message: { Text(toast ?? "") }
        }
    }

    // MARK: 头部

    private var header: some View {
        VStack(spacing: 6) {
            Image(systemName: store.loggedIn ? "person.crop.circle.fill.badge.checkmark" : "person.crop.circle")
                .font(.system(size: 46))
                .foregroundColor(store.loggedIn ? .green : .secondary)
            Text(store.loggedIn ? store.username : "未登录")
                .font(.system(size: 17, weight: .semibold))
            Text(store.loggedIn ? "进度已绑定此账号" : "课程和题目不用登录也能看，登录后进度才会跨设备同步")
                .font(.system(size: 12))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
        }
        .padding(.vertical, 18)
    }

    // MARK: 登录

    private var loginCard: some View {
        VStack(spacing: 12) {
            field("用户名", text: $user, secure: false)
            HStack(spacing: 8) {
                field("密码", text: $pass, secure: !showPass)
                Button {
                    showPass.toggle()
                } label: {
                    Image(systemName: showPass ? "eye.slash" : "eye")
                        .foregroundColor(.secondary)
                }
            }

            if let e = store.authError {
                Text(e).font(.system(size: 12)).foregroundColor(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            Button {
                Task {
                    let ok = await store.doLogin(user, pass)
                    if ok {
                        toast = "登录成功，进度已同步"
                        dismiss()
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    if store.authBusy { ProgressView().tint(.white).scaleEffect(0.8) }
                    Text(store.authBusy ? "登录中…" : "登录")
                        .font(.system(size: 15, weight: .semibold))
                }
                .frame(maxWidth: .infinity).padding(.vertical, 12)
                .background(canSubmit ? Color.accentColor : Color.gray.opacity(0.4))
                .foregroundColor(.white)
                .cornerRadius(11)
            }
            .disabled(!canSubmit)

            Button {
                showRegister = true
            } label: {
                Text(registerLabel)
                    .font(.system(size: 12.5))
                    .foregroundColor(store.registerOpen ? .accentColor : .secondary)
            }
            .disabled(!store.registerOpen)
        }
        .padding(16)
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(14)
        .sheet(isPresented: $showRegister) { registerSheet }
    }

    private var canSubmit: Bool {
        !store.authBusy && !user.trimmingCharacters(in: .whitespaces).isEmpty && pass.count >= 6
    }

    private var registerLabel: String {
        store.registerOpen ? "还没有账号？去注册" : "注册暂未开放"
    }

    // MARK: 已登录

    private var loggedInCards: some View {
        VStack(spacing: 12) {
            VStack(spacing: 0) {
                row("账号", store.username)
                Divider().padding(.leading, 14)
                row("服务器", HubClient.shared.baseURL)
                Divider().padding(.leading, 14)
                row("本地进度", "\(store.progress.count) 条")
                Divider().padding(.leading, 14)
                row("错题", "\(store.wrongs.count) 道")
            }
            .background(Color(.secondarySystemGroupedBackground))
            .cornerRadius(14)

            HStack(spacing: 10) {
                Button {
                    Task { await store.syncUp() }
                } label: {
                    HStack(spacing: 6) {
                        if store.syncing { ProgressView().scaleEffect(0.7) }
                        Text(store.syncing ? "同步中…" : "立即同步")
                            .font(.system(size: 14, weight: .semibold))
                    }
                    .frame(maxWidth: .infinity).padding(.vertical, 11)
                    .background(Color.accentColor).foregroundColor(.white).cornerRadius(11)
                }
                .disabled(store.syncing)

                Button {
                    Task {
                        await store.syncDown()
                        toast = "已拉取云端进度"
                    }
                } label: {
                    Text("拉取")
                        .font(.system(size: 14, weight: .semibold))
                        .frame(width: 74).padding(.vertical, 11)
                        .background(Color(.secondarySystemGroupedBackground)).cornerRadius(11)
                }
                .disabled(store.syncing)
            }

            if let m = store.syncMsg {
                Text(m).font(.system(size: 12)).foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            Button(role: .destructive) {
                Task {
                    await store.doLogout()
                    toast = "已退出登录"
                }
            } label: {
                Text("退出登录")
                    .font(.system(size: 14, weight: .medium))
                    .frame(maxWidth: .infinity).padding(.vertical, 11)
                    .background(Color(.secondarySystemGroupedBackground))
                    .foregroundColor(.red).cornerRadius(11)
            }
        }
    }

    // MARK: 注册

    private var registerSheet: some View {
        NavigationView {
            VStack(spacing: 12) {
                field("用户名（3-32 位字母数字）", text: $regUser, secure: false)
                field("密码（至少 6 位）", text: $regPass, secure: true)
                field("再输一次", text: $regPass2, secure: true)

                if regPass != regPass2 && !regPass2.isEmpty {
                    Text("两次密码不一致").font(.system(size: 12)).foregroundColor(.red)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                if let e = store.authError {
                    Text(e).font(.system(size: 12)).foregroundColor(.red)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                Button {
                    guard regPass == regPass2 else { return }
                    Task {
                        let ok = await store.doRegister(regUser, regPass)
                        if ok {
                            showRegister = false
                            toast = "注册成功"
                        }
                    }
                } label: {
                    Text("注册")
                        .font(.system(size: 15, weight: .semibold))
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(regPass.count >= 6 && regPass == regPass2 ? Color.accentColor : Color.gray.opacity(0.4))
                        .foregroundColor(.white).cornerRadius(11)
                }
                .disabled(store.authBusy || regPass.count < 6 || regPass != regPass2)

                Spacer()
            }
            .padding(16)
            .navigationTitle("注册")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { showRegister = false }
                }
            }
        }
    }

    // MARK: 组件

    private func field(_ ph: String, text: Binding<String>, secure: Bool) -> some View {
        Group {
            if secure {
                SecureField(ph, text: text)
            } else {
                TextField(ph, text: text)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
            }
        }
        .padding(12)
        .background(Color(.tertiarySystemGroupedBackground))
        .cornerRadius(10)
        .font(.system(size: 14))
    }

    private func row(_ k: String, _ v: String) -> some View {
        HStack {
            Text(k).font(.system(size: 13.5)).foregroundColor(.secondary)
            Spacer()
            Text(v).font(.system(size: 13)).lineLimit(1).truncationMode(.middle)
        }
        .padding(.horizontal, 14).padding(.vertical, 11)
    }

    private var footNote: some View {
        Text("课程内容与题目对所有人开放。登录只用于同步你自己的答题进度、错题和笔记，不同账号之间互相看不到。")
            .font(.system(size: 11.5))
            .foregroundColor(.secondary)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 12)
    }
}
