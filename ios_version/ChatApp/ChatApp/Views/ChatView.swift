import SwiftUI

struct ChatView: View {
    @Binding var currentUser: String
    let chatWithUser: String
    
    @State private var messages: [ChatMessage] = []
    @State private var messageText = ""
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showingAlert = false
    @State private var isSending = false
    @State private var refreshID = UUID()
    @State private var showingFileShare = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 消息列表
                if isLoading && messages.isEmpty {
                    ProgressView("加载中...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 10) {
                                ForEach(messages, id: \.id) { message in
                                    MessageRow(message: message, isCurrentUser: message.sender == currentUser)
                                        .id(message.id)
                                }
                            }
                            .padding()
                        }
                        .onChange(of: messages.count) { _ in
                            // 当有新消息时，滚动到底部
                            withAnimation {
                                if let lastMessage = messages.last {
                                    proxy.scrollTo(lastMessage.id, anchor: .bottom)
                                }
                            }
                        }
                    }
                }
                
                // 输入区域
                MessageInputView(
                    messageText: $messageText,
                    isSending: $isSending,
                    onSend: {
                        sendMessage()
                    },
                    onFileShare: {
                        showingFileShare = true
                    }
                )
                .padding(.horizontal)
                .padding(.vertical, 8)
                .background(Color(UIColor.systemBackground))
                .shadow(radius: 1)
            }
            .navigationTitle(chatWithUser)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("返回") {
                        // 关闭视图
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        loadMessages()
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                loadMessages()
            }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
                loadMessages()
            }
            .alert(isPresented: $showingAlert) {
                Alert(title: Text("提示"), message: Text(errorMessage), dismissButton: .default(Text("确定")))
            }
            .sheet(isPresented: $showingFileShare) {
                FileShareView(
                    currentUser: $currentUser,
                    chatWithUser: chatWithUser,
                    isPresented: $showingFileShare
                )
                .onDisappear {
                    // 文件分享完成后刷新消息列表
                    loadMessages()
                }
            }
            .id(refreshID)
        }
    }
    
    private func loadMessages() {
        isLoading = true
        
        Task {
            do {
                let chatMessages = try await NetworkManager.shared.getChatMessages(withUser: chatWithUser)
                
                await MainActor.run {
                    isLoading = false
                    messages = chatMessages
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "加载消息失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
    
    private func sendMessage() {
        guard !messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        isSending = true
        let messageToSend = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        
        Task {
            do {
                let response = try await NetworkManager.shared.sendMessage(
                    receiver: chatWithUser,
                    message: messageToSend
                )
                
                await MainActor.run {
                    isSending = false
                    
                    if response.success {
                        // 发送成功，清空输入框并重新加载消息
                        messageText = ""
                        loadMessages()
                    } else {
                        errorMessage = response.message
                        showingAlert = true
                    }
                }
            } catch {
                await MainActor.run {
                    isSending = false
                    errorMessage = "发送消息失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
}

struct MessageRow: View {
    let message: ChatMessage
    let isCurrentUser: Bool
    
    var body: some View {
        HStack {
            if isCurrentUser {
                Spacer()
                
                messageContent
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(18)
                    .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .trailing)
            } else {
                messageContent
                    .background(Color.gray.opacity(0.2))
                    .foregroundColor(.primary)
                    .cornerRadius(18)
                    .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .leading)
                
                Spacer()
            }
        }
        .padding(.horizontal, 10)
    }
    
    @ViewBuilder
    private var messageContent: some View {
        VStack(alignment: isCurrentUser ? .trailing : .leading, spacing: 4) {
            if message.type == "text" {
                Text(message.content)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
            } else if message.type == "image" {
                // 图片消息
                AsyncImage(url: URL(string: message.content)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 200, height: 200)
                        .cornerRadius(12)
                        .clipped()
                } placeholder: {
                    ProgressView()
                        .frame(width: 200, height: 200)
                        .background(Color.gray.opacity(0.3))
                        .cornerRadius(12)
                }
            } else if message.type == "file" {
                // 文件消息
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "doc.fill")
                            .font(.title2)
                        Text(message.content)
                            .font(.body)
                            .lineLimit(1)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                }
            }
            
            Text(message.time)
                .font(.caption2)
                .foregroundColor(isCurrentUser ? .white.opacity(0.7) : .secondary)
                .padding(.horizontal, 16)
                .padding(.bottom, 4)
        }
    }
}

struct MessageInputView: View {
    @Binding var messageText: String
    @Binding var isSending: Bool
    let onSend: () -> Void
    let onFileShare: () -> Void
    
    @State private var showingFileShare = false
    
    var body: some View {
        HStack(spacing: 12) {
            // 文件分享按钮
            Button(action: {
                showingFileShare = true
            }) {
                Image(systemName: "paperclip")
                    .font(.title2)
                    .foregroundColor(.blue)
            }
            .sheet(isPresented: $showingFileShare) {
                FileShareView(
                    currentUser: .constant(""),
                    chatWithUser: .constant(""),
                    isPresented: $showingFileShare
                )
            }
            
            // 文本输入框
            TextField("输入消息...", text: $messageText)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .disabled(isSending)
            
            // 发送按钮
            Button(action: onSend) {
                if isSending {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(0.8)
                } else {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                        .foregroundColor(.blue)
                }
            }
            .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isSending)
        }
    }
}

#Preview {
    ChatView(currentUser: .constant("user1"), chatWithUser: "user2")
}