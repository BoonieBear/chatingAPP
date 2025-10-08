import SwiftUI

struct ChatListView: View {
    @Binding var currentUser: String
    @Binding var isLoggedIn: Bool
    
    @State private var chatUsers: [ChatUser] = []
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showingAlert = false
    @State private var selectedUser: String?
    @State private var showingChat = false
    @State private var refreshID = UUID()
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading && chatUsers.isEmpty {
                    ProgressView("加载中...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if chatUsers.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "message.circle")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("暂无聊天记录")
                            .font(.headline)
                            .foregroundColor(.gray)
                        
                        Text("开始与朋友聊天吧")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(chatUsers, id: \.name) { user in
                        ChatUserRow(user: user)
                            .onTapGesture {
                                selectedUser = user.name
                                showingChat = true
                            }
                    }
                    .listStyle(PlainListStyle())
                    .refreshable {
                        await loadChatUsers()
                    }
                }
            }
            .navigationTitle("聊天")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isLoggedIn = false
                        UserDefaults.standard.removeObject(forKey: "currentUser")
                    }) {
                        Image(systemName: "arrow.right.square")
                            .font(.title2)
                    }
                }
            }
            .onAppear {
                if chatUsers.isEmpty {
                    loadChatUsers()
                }
            }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
                loadChatUsers()
            }
            .alert(isPresented: $showingAlert) {
                Alert(title: Text("提示"), message: Text(errorMessage), dismissButton: .default(Text("确定")))
            }
            .sheet(isPresented: $showingChat) {
                if let user = selectedUser {
                    ChatView(currentUser: $currentUser, chatWithUser: user)
                }
            }
            .id(refreshID) // 用于强制刷新视图
        }
    }
    
    private func loadChatUsers() {
        isLoading = true
        
        Task {
            do {
                let users = try await NetworkManager.shared.getChatUsers()
                
                await MainActor.run {
                    isLoading = false
                    chatUsers = users
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "加载聊天列表失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
}

struct ChatUserRow: View {
    let user: ChatUser
    
    var body: some View {
        HStack(spacing: 15) {
            // 头像
            ZStack {
                Circle()
                    .fill(Color.blue.opacity(0.1))
                    .frame(width: 50, height: 50)
                
                Text(String(user.name.prefix(1)))
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(.blue)
            }
            
            // 用户信息
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(user.name)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Spacer()
                    
                    if user.hasUnread {
                        Circle()
                            .fill(Color.red)
                            .frame(width: 10, height: 10)
                    }
                }
                
                Text("点击开始聊天")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            
            Spacer()
            
            // 箭头图标
            Image(systemName: "chevron.right")
                .font(.body)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 8)
        .contentShape(Rectangle())
    }
}

#Preview {
    ChatListView(currentUser: .constant("testuser"), isLoggedIn: .constant(true))
}