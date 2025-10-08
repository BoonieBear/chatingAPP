import SwiftUI
import PhotosUI

struct MomentsView: View {
    @Binding var currentUser: String
    
    @State private var moments: [Moment] = []
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showingAlert = false
    @State private var showingNewMoment = false
    @State private var refreshID = UUID()
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading && moments.isEmpty {
                    ProgressView("加载中...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if moments.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "person.2")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("暂无朋友圈")
                            .font(.headline)
                            .foregroundColor(.gray)
                        
                        Text("发布第一条朋友圈吧")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollView {
                        LazyVStack(spacing: 20) {
                            ForEach(moments, id: \.id) { moment in
                                MomentRow(moment: moment, currentUser: currentUser) {
                                    loadMoments()
                                }
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        await loadMoments()
                    }
                }
            }
            .navigationTitle("朋友圈")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingNewMoment = true
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                    }
                }
            }
            .onAppear {
                if moments.isEmpty {
                    loadMoments()
                }
            }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
                loadMoments()
            }
            .alert(isPresented: $showingAlert) {
                Alert(title: Text("提示"), message: Text(errorMessage), dismissButton: .default(Text("确定")))
            }
            .sheet(isPresented: $showingNewMoment) {
                NewMomentView { success in
                    if success {
                        loadMoments()
                    }
                }
            }
            .id(refreshID)
        }
    }
    
    private func loadMoments() {
        isLoading = true
        
        Task {
            do {
                let momentsList = try await NetworkManager.shared.getMoments()
                
                await MainActor.run {
                    isLoading = false
                    moments = momentsList
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "加载朋友圈失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
}

struct MomentRow: View {
    let moment: Moment
    let currentUser: String
    let onRefresh: () -> Void
    
    @State private var showingComments = false
    @State private var commentText = ""
    @State private var isLiking = false
    @State private var isCommenting = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 用户信息
            HStack(spacing: 12) {
                // 头像
                ZStack {
                    Circle()
                        .fill(Color.blue.opacity(0.1))
                        .frame(width: 40, height: 40)
                    
                    Text(String(moment.userName.prefix(1)))
                        .font(.headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.blue)
                }
                
                // 用户名和位置
                VStack(alignment: .leading, spacing: 2) {
                    Text(moment.userName)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    HStack(spacing: 4) {
                        Image(systemName: "location.fill")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text(moment.userInfo.place)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // 时间
                Text(formatTime(moment.postTime))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            // 内容
            if !moment.content.isEmpty {
                Text(moment.content)
                    .font(.body)
                    .foregroundColor(.primary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            // 图片
            if let imagePath = moment.imagePath {
                AsyncImage(url: URL(string: "http://127.0.0.1:5000/static/\(imagePath)")) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(maxHeight: 300)
                        .cornerRadius(12)
                        .clipped()
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 200)
                        .cornerRadius(12)
                        .overlay(
                            ProgressView()
                        )
                }
            }
            
            // 点赞和评论
            HStack(spacing: 20) {
                // 点赞
                Button(action: toggleLike) {
                    HStack(spacing: 4) {
                        Image(systemName: moment.userLiked ? "heart.fill" : "heart")
                            .font(.body)
                            .foregroundColor(moment.userLiked ? .red : .secondary)
                        
                        Text("\(moment.likeCount)")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                }
                .disabled(isLiking)
                
                // 评论
                Button(action: {
                    showingComments = true
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: "bubble.right")
                            .font(.body)
                            .foregroundColor(.secondary)
                        
                        Text("\(moment.comments.count)")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
            }
            
            // 评论列表
            if !moment.comments.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(moment.comments, id: \.commentTime) { comment in
                        HStack(alignment: .top, spacing: 8) {
                            Text(comment.userName + ":")
                                .font(.body)
                                .fontWeight(.medium)
                                .foregroundColor(.blue)
                            
                            Text(comment.comment)
                                .font(.body)
                                .foregroundColor(.primary)
                            
                            Spacer()
                        }
                    }
                }
                .padding(.top, 8)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
            }
        }
        .padding()
        .background(Color(UIColor.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
        .sheet(isPresented: $showingComments) {
            CommentView(
                moment: moment,
                currentUser: currentUser,
                commentText: $commentText,
                isCommenting: $isCommenting
            ) {
                addComment()
            }
        }
    }
    
    private func toggleLike() {
        isLiking = true
        
        Task {
            do {
                let response = try await NetworkManager.shared.likeMoment(momentId: "\(moment.id)")
                
                await MainActor.run {
                    isLiking = false
                    
                    if response.success {
                        onRefresh()
                    }
                }
            } catch {
                await MainActor.run {
                    isLiking = false
                }
            }
        }
    }
    
    private func addComment() {
        guard !commentText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        isCommenting = true
        let commentToSend = commentText.trimmingCharacters(in: .whitespacesAndNewlines)
        
        Task {
            do {
                let response = try await NetworkManager.shared.commentMoment(
                    momentId: "\(moment.id)",
                    comment: commentToSend
                )
                
                await MainActor.run {
                    isCommenting = false
                    
                    if response.success {
                        commentText = ""
                        showingComments = false
                        onRefresh()
                    }
                }
            } catch {
                await MainActor.run {
                    isCommenting = false
                }
            }
        }
    }
    
    private func formatTime(_ timeString: String) -> String {
        // 简单的时间格式化
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        
        if let date = formatter.date(from: timeString) {
            let now = Date()
            let interval = now.timeIntervalSince(date)
            
            if interval < 60 {
                return "刚刚"
            } else if interval < 3600 {
                return "\(Int(interval / 60))分钟前"
            } else if interval < 86400 {
                return "\(Int(interval / 3600))小时前"
            } else {
                formatter.dateFormat = "MM-dd HH:mm"
                return formatter.string(from: date)
            }
        }
        
        return timeString
    }
}

struct NewMomentView: View {
    @Environment(\.presentationMode) var presentationMode
    let onPost: (Bool) -> Void
    
    @State private var content = ""
    @State private var selectedImage: PhotosPickerItem?
    @State private var selectedImageData: Data?
    @State private var isPosting = false
    
    var body: some View {
        NavigationView {
            VStack {
                // 文本输入
                TextField("分享你的想法...", text: $content, axis: .vertical)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .lineLimit(8)
                    .padding()
                
                // 图片选择
                if let selectedImageData = selectedImageData,
                   let uiImage = UIImage(data: selectedImageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(height: 200)
                        .cornerRadius(12)
                        .clipped()
                        .padding(.horizontal)
                }
                
                Spacer()
            }
            .navigationTitle("发布朋友圈")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: postMoment) {
                        if isPosting {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(0.8)
                        } else {
                            Text("发布")
                                .fontWeight(.semibold)
                        }
                    }
                    .disabled(content.isEmpty || isPosting)
                }
            }
            .photosPicker(
                isPresented: Binding(
                    get: { selectedImage != nil },
                    set: { _ in }
                ),
                selection: $selectedImage,
                matching: .images,
                photoLibrary: .shared()
            )
            .onChange(of: selectedImage) { newItem in
                Task {
                    if let data = try? await newItem?.loadTransferable(type: Data.self) {
                        selectedImageData = data
                    }
                }
            }
        }
    }
    
    private func postMoment() {
        isPosting = true
        
        Task {
            do {
                let response = try await NetworkManager.shared.postMoment(
                    content: content,
                    imageData: selectedImageData
                )
                
                await MainActor.run {
                    isPosting = false
                    
                    if response.success {
                        onPost(true)
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            } catch {
                await MainActor.run {
                    isPosting = false
                }
            }
        }
    }
}

struct CommentView: View {
    let moment: Moment
    let currentUser: String
    @Binding var commentText: String
    @Binding var isCommenting: Bool
    let onComment: () -> Void
    
    var body: some View {
        NavigationView {
            VStack {
                // 原朋友圈内容预览
                VStack(alignment: .leading, spacing: 8) {
                    Text(moment.userName)
                        .font(.headline)
                    
                    Text(moment.content)
                        .font(.body)
                        .lineLimit(3)
                    
                    if let imagePath = moment.imagePath {
                        AsyncImage(url: URL(string: "http://127.0.0.1:5000/static/\(imagePath)")) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(height: 150)
                                .cornerRadius(8)
                                .clipped()
                        } placeholder: {
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(height: 150)
                                .cornerRadius(8)
                        }
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
                .padding()
                
                // 评论列表
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        ForEach(moment.comments, id: \.commentTime) { comment in
                            HStack(alignment: .top, spacing: 8) {
                                Text(comment.userName + ":")
                                    .font(.body)
                                    .fontWeight(.medium)
                                    .foregroundColor(.blue)
                                
                                Text(comment.comment)
                                    .font(.body)
                                    .foregroundColor(.primary)
                                
                                Spacer()
                            }
                            .padding(.horizontal)
                        }
                    }
                }
                
                // 输入评论
                HStack(spacing: 12) {
                    TextField("写评论...", text: $commentText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .disabled(isCommenting)
                    
                    Button(action: onComment) {
                        if isCommenting {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .blue))
                                .scaleEffect(0.8)
                        } else {
                            Text("发送")
                                .fontWeight(.semibold)
                                .foregroundColor(.blue)
                        }
                    }
                    .disabled(commentText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isCommenting)
                }
                .padding()
            }
            .navigationTitle("评论")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("完成") {
                        // 关闭视图
                    }
                }
            }
        }
    }
}

#Preview {
    MomentsView(currentUser: .constant("testuser"))
}