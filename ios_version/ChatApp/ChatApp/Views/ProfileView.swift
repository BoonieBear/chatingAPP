import SwiftUI
import PhotosUI

struct ProfileView: View {
    @Binding var currentUser: String
    @Binding var isLoggedIn: Bool
    
    @State private var userProfile: UserProfile?
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showingAlert = false
    @State private var selectedAvatar: PhotosPickerItem?
    @State private var selectedAvatarData: Data?
    @State private var isEditing = false
    @State private var refreshID = UUID()
    
    // 编辑字段
    @State private var bio = ""
    @State private var birthDate = ""
    @State private var themePreference = "light"
    @State private var notificationEnabled = true
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading && userProfile == nil {
                    ProgressView("加载中...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollView {
                        VStack(spacing: 20) {
                            // 头像区域
                            VStack(spacing: 16) {
                                ZStack {
                                    Circle()
                                        .fill(Color.blue.opacity(0.1))
                                        .frame(width: 100, height: 100)
                                    
                                    if let avatarData = selectedAvatarData,
                                       let uiImage = UIImage(data: avatarData) {
                                        Image(uiImage: uiImage)
                                            .resizable()
                                            .aspectRatio(contentMode: .fill)
                                            .frame(width: 100, height: 100)
                                            .clipShape(Circle())
                                    } else if let avatarPath = userProfile?.avatarPath {
                                        AsyncImage(url: URL(string: "http://127.0.0.1:5000/static/\(avatarPath)")) { image in
                                            image
                                                .resizable()
                                                .aspectRatio(contentMode: .fill)
                                                .frame(width: 100, height: 100)
                                                .clipShape(Circle())
                                        } placeholder: {
                                            Circle()
                                                .fill(Color.blue.opacity(0.1))
                                                .frame(width: 100, height: 100)
                                                .overlay(
                                                    Text(String(currentUser.prefix(1)))
                                                        .font(.title)
                                                        .fontWeight(.semibold)
                                                        .foregroundColor(.blue)
                                                )
                                        }
                                    } else {
                                        Text(String(currentUser.prefix(1)))
                                            .font(.title)
                                            .fontWeight(.semibold)
                                            .foregroundColor(.blue)
                                    }
                                }
                                
                                Text(currentUser)
                                    .font(.title)
                                    .fontWeight(.bold)
                                
                                if isEditing {
                                    PhotosPicker(
                                        selection: $selectedAvatar,
                                        matching: .images,
                                        photoLibrary: .shared()
                                    ) {
                                        Text("更换头像")
                                            .font(.body)
                                            .foregroundColor(.blue)
                                    }
                                    .onChange(of: selectedAvatar) { newItem in
                                        Task {
                                            if let data = try? await newItem?.loadTransferable(type: Data.self) {
                                                selectedAvatarData = data
                                            }
                                        }
                                    }
                                }
                            }
                            .padding()
                            
                            // 个人信息区域
                            VStack(spacing: 16) {
                                if isEditing {
                                   编辑字段
                                    // 编辑字段
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("个人简介")
                                            .font(.headline)
                                            .foregroundColor(.primary)
                                        
                                        TextField("介绍一下自己...", text: $bio, axis: .vertical)
                                            .textFieldStyle(RoundedBorderTextFieldStyle())
                                            .lineLimit(4)
                                    }
                                    
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("生日")
                                            .font(.headline)
                                            .foregroundColor(.primary)
                                        
                                        TextField("YYYY-MM-DD", text: $birthDate)
                                            .textFieldStyle(RoundedBorderTextFieldStyle())
                                    }
                                    
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("主题偏好")
                                            .font(.headline)
                                            .foregroundColor(.primary)
                                        
                                        Picker("主题偏好", selection: $themePreference) {
                                            Text("浅色").tag("light")
                                            Text("深色").tag("dark")
                                            Text("跟随系统").tag("auto")
                                        }
                                        .pickerStyle(SegmentedPickerStyle())
                                    }
                                    
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("通知设置")
                                            .font(.headline)
                                            .foregroundColor(.primary)
                                        
                                        Toggle("接收通知", isOn: $notificationEnabled)
                                            .toggleStyle(SwitchToggleStyle(tint: .blue))
                                    }
                                } else {
                                    // 显示个人信息
                                    if let bio = userProfile?.bio, !bio.isEmpty {
                                        VStack(alignment: .leading, spacing: 8) {
                                            Text("个人简介")
                                                .font(.headline)
                                                .foregroundColor(.primary)
                                            
                                            Text(bio)
                                                .font(.body)
                                                .foregroundColor(.secondary)
                                                .frame(maxWidth: .infinity, alignment: .leading)
                                        }
                                        .padding()
                                        .background(Color.gray.opacity(0.1))
                                        .cornerRadius(8)
                                    }
                                    
                                    if let birthDate = userProfile?.birthDate, !birthDate.isEmpty {
                                        VStack(alignment: .leading, spacing: 8) {
                                            HStack {
                                                Image(systemName: "calendar")
                                                    .font(.body)
                                                    .foregroundColor(.secondary)
                                                
                                                Text("生日")
                                                    .font(.headline)
                                                    .foregroundColor(.primary)
                                                
                                                Spacer()
                                                
                                                Text(birthDate)
                                                    .font(.body)
                                                    .foregroundColor(.secondary)
                                            }
                                        }
                                        .padding()
                                        .background(Color.gray.opacity(0.1))
                                        .cornerRadius(8)
                                    }
                                    
                                    VStack(alignment: .leading, spacing: 8) {
                                        HStack {
                                            Image(systemName: "paintbrush.fill")
                                                .font(.body)
                                                .foregroundColor(.secondary)
                                            
                                            Text("主题偏好")
                                                .font(.headline)
                                                .foregroundColor(.primary)
                                            
                                            Spacer()
                                            
                                            Text(themePreferenceText)
                                                .font(.body)
                                                .foregroundColor(.secondary)
                                        }
                                    }
                                    .padding()
                                    .background(Color.gray.opacity(0.1))
                                    .cornerRadius(8)
                                    
                                    VStack(alignment: .leading, spacing: 8) {
                                        HStack {
                                            Image(systemName: "bell.fill")
                                                .font(.body)
                                                .foregroundColor(.secondary)
                                            
                                            Text("通知设置")
                                                .font(.headline)
                                                .foregroundColor(.primary)
                                            
                                            Spacer()
                                            
                                            Text(notificationEnabled ? "已开启" : "已关闭")
                                                .font(.body)
                                                .foregroundColor(notificationEnabled ? .green : .red)
                                        }
                                    }
                                    .padding()
                                    .background(Color.gray.opacity(0.1))
                                    .cornerRadius(8)
                                }
                            }
                            .padding()
                            
                            // 操作按钮
                            VStack(spacing: 16) {
                                Button(action: {
                                    if isEditing {
                                        saveProfile()
                                    } else {
                                        startEditing()
                                    }
                                }) {
                                    Text(isEditing ? "保存" : "编辑资料")
                                        .font(.headline)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 50)
                                        .background(Color.blue)
                                        .cornerRadius(12)
                                }
                                
                                if !isEditing {
                                    Button(action: {
                                        logout()
                                    }) {
                                        Text("退出登录")
                                            .font(.headline)
                                            .foregroundColor(.white)
                                            .frame(maxWidth: .infinity)
                                            .frame(height: 50)
                                            .background(Color.red)
                                            .cornerRadius(12)
                                    }
                                }
                            }
                            .padding()
                        }
                    }
                }
            }
            .navigationTitle("我的")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    if isEditing {
                        Button("取消") {
                            cancelEditing()
                        }
                    }
                }
            }
            .onAppear {
                loadUserProfile()
            }
            .alert(isPresented: $showingAlert) {
                Alert(title: Text("提示"), message: Text(errorMessage), dismissButton: .default(Text("确定")))
            }
            .id(refreshID)
        }
    }
    
    private var themePreferenceText: String {
        switch themePreference {
        case "light":
            return "浅色"
        case "dark":
            return "深色"
        case "auto":
            return "跟随系统"
        default:
            return "浅色"
        }
    }
    
    private func loadUserProfile() {
        isLoading = true
        
        Task {
            do {
                let profile = try await NetworkManager.shared.getUserProfile()
                
                await MainActor.run {
                    isLoading = false
                    userProfile = profile
                    
                    // 初始化编辑字段
                    bio = profile.bio ?? ""
                    birthDate = profile.birthDate ?? ""
                    themePreference = profile.themePreference
                    notificationEnabled = profile.notificationEnabled
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "加载个人资料失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
    
    private func startEditing() {
        isEditing = true
    }
    
    private func cancelEditing() {
        isEditing = false
        selectedAvatarData = nil
        
        // 恢复原始值
        if let profile = userProfile {
            bio = profile.bio ?? ""
            birthDate = profile.birthDate ?? ""
            themePreference = profile.themePreference
            notificationEnabled = profile.notificationEnabled
        }
    }
    
    private func saveProfile() {
        // 这里应该调用API保存用户资料
        // 由于Flask后端没有提供更新用户资料的API，这里只是模拟
        
        isEditing = false
        
        // 更新本地用户资料
        userProfile = UserProfile(
            avatarPath: selectedAvatarData != nil ? "updated_avatar.jpg" : userProfile?.avatarPath,
            bio: bio.isEmpty ? nil : bio,
            birthDate: birthDate.isEmpty ? nil : birthDate,
            themePreference: themePreference,
            notificationEnabled: notificationEnabled
        )
        
        errorMessage = "个人资料已更新"
        showingAlert = true
        
        // 应用主题设置
        applyThemeSettings()
    }
    
    private func applyThemeSettings() {
        // 应用主题设置
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first else { return }
        
        switch themePreference {
        case "light":
            window.overrideUserInterfaceStyle = .light
        case "dark":
            window.overrideUserInterfaceStyle = .dark
        case "auto":
            window.overrideUserInterfaceStyle = .unspecified
        default:
            window.overrideUserInterfaceStyle = .unspecified
        }
    }
    
    private func logout() {
        isLoggedIn = false
        UserDefaults.standard.removeObject(forKey: "currentUser")
    }
}

#Preview {
    ProfileView(currentUser: .constant("testuser"), isLoggedIn: .constant(true))
}