import SwiftUI
import UniformTypeIdentifiers
import PhotosUI

struct FileShareView: View {
    @Binding var currentUser: String
    @Binding var chatWithUser: String
    @Binding var isPresented: Bool
    
    @State private var selectedFile: PhotosPickerItem?
    @State private var selectedFileData: Data?
    @State private var fileName = ""
    @State private var isSending = false
    @State private var errorMessage = ""
    @State private var showingAlert = false
    @State private var showingSuccess = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // 文件选择区域
                VStack(spacing: 20) {
                    if let fileData = selectedFileData, !fileName.isEmpty {
                        VStack(spacing: 16) {
                            // 文件图标
                            Image(systemName: fileIcon(for: fileName))
                                .font(.system(size: 60))
                                .foregroundColor(.blue)
                            
                            // 文件名
                            Text(fileName)
                                .font(.headline)
                                .foregroundColor(.primary)
                                .multilineTextAlignment(.center)
                            
                            // 文件大小
                            Text(formatFileSize(fileData.count))
                                .font(.body)
                                .foregroundColor(.secondary)
                            
                            // 重新选择按钮
                            Button("重新选择") {
                                selectedFile = nil
                                selectedFileData = nil
                                fileName = ""
                            }
                            .foregroundColor(.blue)
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                    } else {
                        VStack(spacing: 16) {
                            Image(systemName: "doc.badge.plus")
                                .font(.system(size: 60))
                                .foregroundColor(.gray)
                            
                            Text("选择要分享的文件")
                                .font(.headline)
                                .foregroundColor(.primary)
                            
                            Text("支持各种文件类型")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                        .padding(40)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                        .onTapGesture {
                            // 触发文件选择
                        }
                    }
                }
                
                Spacer()
                
                // 操作按钮
                VStack(spacing: 16) {
                    if selectedFileData == nil {
                        PhotosPicker(
                            selection: $selectedFile,
                            matching: .any(of: [.images, .videos, .pdfs, .text, .spreadsheets, .presentations]),
                            photoLibrary: .shared()
                        ) {
                            HStack {
                                Image(systemName: "folder")
                                    .font(.title2)
                                
                                Text("选择文件")
                                    .font(.headline)
                            }
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(Color.blue)
                            .cornerRadius(12)
                        }
                        .onChange(of: selectedFile) { newItem in
                            Task {
                                if let data = try? await newItem?.loadTransferable(type: Data.self) {
                                    selectedFileData = data
                                    fileName = newItem?.itemIdentifier ?? "未知文件"
                                }
                            }
                        }
                    } else {
                        Button(action: sendFile) {
                            HStack {
                                if isSending {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                        .scaleEffect(0.8)
                                } else {
                                    Image(systemName: "paperplane.fill")
                                        .font(.title2)
                                }
                                
                                Text("发送文件")
                                    .font(.headline)
                            }
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(Color.green)
                            .cornerRadius(12)
                        }
                        .disabled(isSending)
                    }
                    
                    Button("取消") {
                        isPresented = false
                    }
                    .foregroundColor(.red)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                }
                .padding()
            }
            .padding()
            .navigationTitle("分享文件")
            .navigationBarTitleDisplayMode(.inline)
            .alert(isPresented: $showingAlert) {
                Alert(title: Text("错误"), message: Text(errorMessage), dismissButton: .default(Text("确定")))
            }
            .alert(isPresented: $showingSuccess) {
                Alert(title: Text("成功"), message: Text("文件已发送"), dismissButton: .default(Text("确定")) {
                    isPresented = false
                })
            }
        }
    }
    
    private func fileIcon(for fileName: String) -> String {
        let ext = (fileName as NSString).pathExtension.lowercased()
        
        switch ext {
        case "pdf":
            return "doc.fill"
        case "doc", "docx":
            return "doc.text.fill"
        case "xls", "xlsx":
            return "chart.bar.fill"
        case "ppt", "pptx":
            return "play.rectangle.fill"
        case "jpg", "jpeg", "png", "gif", "heic":
            return "photo.fill"
        case "mp4", "mov", "avi":
            return "video.fill"
        case "mp3", "wav", "aac":
            return "music.note"
        case "zip", "rar", "7z":
            return "archivebox.fill"
        case "txt", "md":
            return "doc.text.fill"
        default:
            return "doc.fill"
        }
    }
    
    private func formatFileSize(_ bytes: Int) -> String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        return formatter.string(fromByteCount: Int64(bytes))
    }
    
    private func sendFile() {
        guard let fileData = selectedFileData else { return }
        
        isSending = true
        
        Task {
            do {
                // 这里应该调用API发送文件
                // 由于Flask后端需要multipart/form-data，这里需要特殊处理
                let url = URL(string: "http://127.0.0.1:5000/send_file")!
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                
                // 创建多部分表单数据
                let boundary = UUID().uuidString
                request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
                
                var body = Data()
                
                // 添加接收者字段
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"receiver\"\r\n\r\n".data(using: .utf8)!)
                body.append("\(chatWithUser)\r\n".data(using: .utf8)!)
                
                // 添加文件字段
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
                body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
                body.append(fileData)
                body.append("\r\n".data(using: .utf8)!)
                
                body.append("--\(boundary)--\r\n".data(using: .utf8)!)
                request.httpBody = body
                
                let (_, response) = try await URLSession.shared.data(for: request)
                
                await MainActor.run {
                    isSending = false
                    
                    if let httpResponse = response as? HTTPURLResponse,
                       httpResponse.statusCode == 200 {
                        showingSuccess = true
                    } else {
                        errorMessage = "发送文件失败，请重试"
                        showingAlert = true
                    }
                }
            } catch {
                await MainActor.run {
                    isSending = false
                    errorMessage = "发送文件失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
}

struct FileMessageView: View {
    let message: ChatMessage
    let isCurrentUser: Bool
    let onDownload: () -> Void
    
    var body: some View {
        HStack {
            if isCurrentUser {
                Spacer()
                
                fileContent
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(18)
                    .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .trailing)
            } else {
                fileContent
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
    private var fileContent: some View {
        VStack(alignment: isCurrentUser ? .trailing : .leading, spacing: 8) {
            HStack {
                Image(systemName: fileIcon(for: message.content))
                    .font(.title2)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(message.content)
                        .font(.body)
                        .lineLimit(1)
                    
                    if let fileSize = extractFileSize(from: message.content) {
                        Text(formatFileSize(fileSize))
                            .font(.caption)
                            .opacity(0.8)
                    }
                }
                
                Spacer()
                
                Button(action: onDownload) {
                    Image(systemName: "arrow.down.circle.fill")
                        .font(.title2)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            
            Text(message.time)
                .font(.caption2)
                .foregroundColor(isCurrentUser ? .white.opacity(0.7) : .secondary)
                .padding(.horizontal, 16)
                .padding(.bottom, 4)
        }
    }
    
    private func fileIcon(for fileName: String) -> String {
        let ext = (fileName as NSString).pathExtension.lowercased()
        
        switch ext {
        case "pdf":
            return "doc.fill"
        case "doc", "docx":
            return "doc.text.fill"
        case "xls", "xlsx":
            return "chart.bar.fill"
        case "ppt", "pptx":
            return "play.rectangle.fill"
        case "jpg", "jpeg", "png", "gif", "heic":
            return "photo.fill"
        case "mp4", "mov", "avi":
            return "video.fill"
        case "mp3", "wav", "aac":
            return "music.note"
        case "zip", "rar", "7z":
            return "archivebox.fill"
        case "txt", "md":
            return "doc.text.fill"
        default:
            return "doc.fill"
        }
    }
    
    private func extractFileSize(from content: String) -> Int? {
        // 这里应该从消息内容中提取文件大小
        // 由于当前实现中没有包含文件大小信息，这里返回nil
        return nil
    }
    
    private func formatFileSize(_ bytes: Int) -> String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        return formatter.string(fromByteCount: Int64(bytes))
    }
}

#Preview {
    FileShareView(currentUser: .constant("user1"), chatWithUser: .constant("user2"), isPresented: .constant(true))
}
