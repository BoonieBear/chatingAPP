import Foundation
import SwiftUI

class NetworkManager: ObservableObject {
    static let shared = NetworkManager()
    
    // 服务器地址 - 根据实际情况修改
    private let baseURL = "http://127.0.0.1:5000"
    
    private init() {}
    
    // MARK: - 登录和注册
    func login(username: String, password: String) async throws -> LoginResponse {
        let url = URL(string: "\(baseURL)/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "username=\(username)&password=\(password)"
        request.httpBody = bodyString.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try parseLoginResponse(data: data)
    }
    
    func register(name: String, password: String, phone: String, place: String, sex: String) async throws -> RegisterResponse {
        let url = URL(string: "\(baseURL)/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "name=\(name)&password=\(password)&password_confirm=\(password)&phone=\(phone)&place=\(place)&sex=\(sex)"
        request.httpBody = bodyString.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try parseRegisterResponse(data: data)
    }
    
    // MARK: - 聊天相关
    func getChatUsers() async throws -> [ChatUser] {
        let url = URL(string: "\(baseURL)/chat_users")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try parseChatUsersResponse(data: data)
    }
    
    func getChatMessages(withUser: String) async throws -> [ChatMessage] {
        let url = URL(string: "\(baseURL)/chat_messages/\(withUser)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try parseChatMessagesResponse(data: data)
    }
    
    func sendMessage(receiver: String, message: String) async throws -> APIResponse {
        let url = URL(string: "\(baseURL)/send_private_message")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "receiver=\(receiver)&message=\(message)"
        request.httpBody = bodyString.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try parseAPIResponse(data: data)
    }
    
    // MARK: - 朋友圈相关
    func getMoments() async throws -> [Moment] {
        let url = URL(string: "\(baseURL)/get_moments")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try parseMomentsResponse(data: data)
    }
    
    func postMoment(content: String, imageData: Data? = nil) async throws -> APIResponse {
        let url = URL(string: "\(baseURL)/post_moment")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // 创建多部分表单数据
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // 添加内容字段
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"content\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(content)\r\n".data(using: .utf8)!)
        
        // 如果有图片，添加图片字段
        if let imageData = imageData {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"image\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
            body.append(imageData)
            body.append("\r\n".data(using: .utf8)!)
        }
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try parseAPIResponse(data: data)
    }
    
    func likeMoment(momentId: String) async throws -> LikeResponse {
        let url = URL(string: "\(baseURL)/like_moment")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "moment_id=\(momentId)"
        request.httpBody = bodyString.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try parseLikeResponse(data: data)
    }
    
    func commentMoment(momentId: String, comment: String) async throws -> APIResponse {
        let url = URL(string: "\(baseURL)/comment_moment")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "moment_id=\(momentId)&comment=\(comment)"
        request.httpBody = bodyString.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try parseAPIResponse(data: data)
    }
    
    // MARK: - 用户相关
    func getUserProfile() async throws -> UserProfile {
        let url = URL(string: "\(baseURL)/get_user_profile")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try parseUserProfileResponse(data: data)
    }
    
    // MARK: - 解析响应数据
    private func parseLoginResponse(data: Data) throws -> LoginResponse {
        guard let htmlString = String(data: data, encoding: .utf8) else {
            throw APIError.invalidResponse
        }
        
        // 简单的HTML解析，检查是否重定向到main页面（登录成功）
        if htmlString.contains("redirect") && htmlString.contains("main") {
            return LoginResponse(success: true)
        } else {
            return LoginResponse(success: false)
        }
    }
    
    private func parseRegisterResponse(data: Data) throws -> RegisterResponse {
        guard let htmlString = String(data: data, encoding: .utf8) else {
            throw APIError.invalidResponse
        }
        
        // 简单的HTML解析，检查是否重定向到login页面（注册成功）
        if htmlString.contains("redirect") && htmlString.contains("login") {
            return RegisterResponse(success: true)
        } else {
            return RegisterResponse(success: false)
        }
    }
    
    private func parseAPIResponse(data: Data) throws -> APIResponse {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw APIError.invalidResponse
        }
        
        return APIResponse(
            success: json["success"] as? Bool ?? false,
            message: json["message"] as? String ?? ""
        )
    }
    
    private func parseChatUsersResponse(data: Data) throws -> [ChatUser] {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let success = json["success"] as? Bool,
              success,
              let usersData = json["data"] as? [[String: Any]] else {
            throw APIError.invalidResponse
        }
        
        return usersData.compactMap { userData in
            guard let name = userData["name"] as? String else { return nil }
            return ChatUser(
                name: name,
                hasUnread: userData["has_unread"] as? Bool ?? false
            )
        }
    }
    
    private func parseChatMessagesResponse(data: Data) throws -> [ChatMessage] {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let success = json["success"] as? Bool,
              success,
              let messagesData = json["data"] as? [[String: Any]] else {
            throw APIError.invalidResponse
        }
        
        return messagesData.compactMap { messageData in
            guard let id = messageData["id"] as? Int,
                  let type = messageData["type"] as? String,
                  let sender = messageData["sender"] as? String,
                  let content = messageData["content"] as? String,
                  let time = messageData["time"] as? String else { return nil }
            
            return ChatMessage(
                id: id,
                type: type,
                sender: sender,
                content: content,
                time: time
            )
        }
    }
    
    private func parseMomentsResponse(data: Data) throws -> [Moment] {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let success = json["success"] as? Bool,
              success,
              let momentsData = json["data"] as? [[String: Any]] else {
            throw APIError.invalidResponse
        }
        
        return momentsData.compactMap { momentData in
            guard let id = momentData["id"] as? Int,
                  let userName = momentData["user_name"] as? String,
                  let content = momentData["content"] as? String,
                  let postTime = momentData["post_time"] as? String,
                  let likeCount = momentData["like_count"] as? Int,
                  let userLiked = momentData["user_liked"] as? Bool else { return nil }
            
            let imagePaths = momentData["image_paths"] as? String
            let userInfo = momentData["user_info"] as? [String: Any]
            let comments = momentData["comments"] as? [[String: Any]] ?? []
            
            return Moment(
                id: id,
                userName: userName,
                content: content,
                imagePath: imagePaths,
                postTime: postTime,
                userInfo: UserInfo(
                    phone: userInfo?["phone"] as? String ?? "",
                    sex: userInfo?["sex"] as? String ?? "",
                    place: userInfo?["place"] as? String ?? ""
                ),
                likeCount: likeCount,
                userLiked: userLiked,
                comments: comments.compactMap { commentData in
                    guard let commentUserName = commentData["user_name"] as? String,
                          let comment = commentData["comment"] as? String,
                          let commentTime = commentData["comment_time"] as? String else { return nil }
                    
                    return MomentComment(
                        userName: commentUserName,
                        comment: comment,
                        commentTime: commentTime
                    )
                }
            )
        }
    }
    
    private func parseLikeResponse(data: Data) throws -> LikeResponse {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let success = json["success"] as? Bool,
              success,
              let action = json["action"] as? String else {
            throw APIError.invalidResponse
        }
        
        return LikeResponse(
            success: success,
            action: action
        )
    }
    
    private func parseUserProfileResponse(data: Data) throws -> UserProfile {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let success = json["success"] as? Bool,
              success,
              let data = json["data"] as? [String: Any] else {
            throw APIError.invalidResponse
        }
        
        return UserProfile(
            avatarPath: data["avatar_path"] as? String,
            bio: data["bio"] as? String,
            birthDate: data["birth_date"] as? String,
            themePreference: data["theme_preference"] as? String ?? "light",
            notificationEnabled: data["notification_enabled"] as? Bool ?? true
        )
    }
}

// MARK: - 数据模型
struct LoginResponse {
    let success: Bool
}

struct RegisterResponse {
    let success: Bool
}

struct APIResponse {
    let success: Bool
    let message: String
}

struct ChatUser {
    let name: String
    let hasUnread: Bool
}

struct ChatMessage {
    let id: Int
    let type: String // text, image, file
    let sender: String
    let content: String
    let time: String
}

struct Moment {
    let id: Int
    let userName: String
    let content: String
    let imagePath: String?
    let postTime: String
    let userInfo: UserInfo
    let likeCount: Int
    let userLiked: Bool
    let comments: [MomentComment]
}

struct UserInfo {
    let phone: String
    let sex: String
    let place: String
}

struct MomentComment {
    let userName: String
    let comment: String
    let commentTime: String
}

struct LikeResponse {
    let success: Bool
    let action: String // like or unlike
}

struct UserProfile {
    let avatarPath: String?
    let bio: String?
    let birthDate: String?
    let themePreference: String
    let notificationEnabled: Bool
}

enum APIError: Error {
    case invalidResponse
    case networkError
}