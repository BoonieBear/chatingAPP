import SwiftUI

struct LoginView: View {
    @Binding var isLoggedIn: Bool
    @Binding var currentUser: String
    
    @State private var username = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showingAlert = false
    
    // 注册字段
    @State private var registerName = ""
    @State private var registerPassword = ""
    @State private var registerConfirmPassword = ""
    @State private var registerPhone = ""
    @State private var registerPlace = ""
    @State private var registerSex = "男"
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Logo区域
                VStack(spacing: 10) {
                    Image(systemName: "message.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.blue)
                    
                    Text("漂流瓶聊天")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                }
                .padding(.top, 50)
                .padding(.bottom, 30)
                
                // 表单区域
                ScrollView {
                    if isRegistering {
                        registerForm
                    } else {
                        loginForm
                    }
                }
                .frame(maxHeight: 400)
                
                Spacer()
                
                // 切换登录/注册
                HStack {
                    Text(isRegistering ? "已有账号？" : "没有账号？")
                        .foregroundColor(.secondary)
                    
                    Button(action: {
                        withAnimation {
                            isRegistering.toggle()
                            clearForm()
                        }
                    }) {
                        Text(isRegistering ? "立即登录" : "立即注册")
                            .fontWeight(.semibold)
                            .foregroundColor(.blue)
                    }
                }
                .padding(.bottom, 50)
            }
            .padding()
            .navigationBarHidden(true)
            .alert(isPresented: $showingAlert) {
                Alert(title: Text("提示"), message: Text(errorMessage), dismissButton: .default(Text("确定")))
            }
        }
    }
    
    private var loginForm: some View {
        VStack(spacing: 20) {
            VStack(alignment: .leading, spacing: 8) {
                Text("用户名")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                TextField("请输入用户名", text: $username)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("密码")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                SecureField("请输入密码", text: $password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }
            
            Button(action: login) {
                HStack {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(0.8)
                    }
                    
                    Text("登录")
                        .font(.headline)
                        .foregroundColor(.white)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(username.isEmpty || password.isEmpty || isLoading ? Color.gray : Color.blue)
                )
            }
            .disabled(username.isEmpty || password.isEmpty || isLoading)
        }
    }
    
    private var registerForm: some View {
        VStack(spacing: 15) {
            VStack(alignment: .leading, spacing: 8) {
                Text("用户名")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                TextField("请输入用户名", text: $registerName)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("密码")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                SecureField("请输入密码", text: $registerPassword)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("确认密码")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                SecureField("请再次输入密码", text: $registerConfirmPassword)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("手机号")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                TextField("请输入手机号", text: $registerPhone)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .keyboardType(.phonePad)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("所在地")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                TextField("请输入所在地", text: $registerPlace)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("性别")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                Picker("性别", selection: $registerSex) {
                    Text("男").tag("男")
                    Text("女").tag("女")
                }
                .pickerStyle(SegmentedPickerStyle())
            }
            
            Button(action: register) {
                HStack {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(0.8)
                    }
                    
                    Text("注册")
                        .font(.headline)
                        .foregroundColor(.white)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(registerName.isEmpty || registerPassword.isEmpty || registerConfirmPassword.isEmpty || registerPhone.isEmpty || registerPlace.isEmpty || isLoading ? Color.gray : Color.blue)
                )
            }
            .disabled(registerName.isEmpty || registerPassword.isEmpty || registerConfirmPassword.isEmpty || registerPhone.isEmpty || registerPlace.isEmpty || isLoading)
        }
    }
    
    private func login() {
        isLoading = true
        
        Task {
            do {
                let response = try await NetworkManager.shared.login(username: username, password: password)
                
                await MainActor.run {
                    isLoading = false
                    
                    if response.success {
                        currentUser = username
                        isLoggedIn = true
                        UserDefaults.standard.set(username, forKey: "currentUser")
                    } else {
                        errorMessage = "用户名或密码错误"
                        showingAlert = true
                    }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "登录失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
    
    private func register() {
        guard registerPassword == registerConfirmPassword else {
            errorMessage = "两次输入的密码不一致"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        Task {
            do {
                let response = try await NetworkManager.shared.register(
                    name: registerName,
                    password: registerPassword,
                    phone: registerPhone,
                    place: registerPlace,
                    sex: registerSex
                )
                
                await MainActor.run {
                    isLoading = false
                    
                    if response.success {
                        // 注册成功，切换到登录界面
                        withAnimation {
                            isRegistering = false
                            clearForm()
                        }
                        errorMessage = "注册成功，请登录"
                        showingAlert = true
                    } else {
                        errorMessage = "注册失败，请重试"
                        showingAlert = true
                    }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "注册失败，请检查网络连接"
                    showingAlert = true
                }
            }
        }
    }
    
    private func clearForm() {
        username = ""
        password = ""
        registerName = ""
        registerPassword = ""
        registerConfirmPassword = ""
        registerPhone = ""
        registerPlace = ""
        registerSex = "男"
        errorMessage = ""
    }
}

#Preview {
    LoginView(isLoggedIn: .constant(false), currentUser: .constant(""))
}