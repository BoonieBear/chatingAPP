import SwiftUI

struct ContentView: View {
    @State private var isLoggedIn = false
    @State private var currentUser: String = ""
    @State private var selectedTab = 0
    
    var body: some View {
        Group {
            if isLoggedIn {
                TabView(selection: $selectedTab) {
                    ChatListView(currentUser: $currentUser, isLoggedIn: $isLoggedIn)
                        .tabItem {
                            Label("聊天", systemImage: "message.fill")
                        }
                        .tag(0)
                    
                    MomentsView(currentUser: $currentUser)
                        .tabItem {
                            Label("朋友圈", systemImage: "person.2.fill")
                        }
                        .tag(1)
                    
                    ProfileView(currentUser: $currentUser, isLoggedIn: $isLoggedIn)
                        .tabItem {
                            Label("我的", systemImage: "person.fill")
                        }
                        .tag(2)
                }
                .accentColor(.blue)
                .onAppear {
                    // 检查登录状态
                    checkLoginStatus()
                }
            } else {
                LoginView(isLoggedIn: $isLoggedIn, currentUser: $currentUser)
            }
        }
    }
    
    private func checkLoginStatus() {
        // 检查本地存储的登录状态
        if let savedUser = UserDefaults.standard.string(forKey: "currentUser") {
            currentUser = savedUser
            isLoggedIn = true
        }
    }
}

#Preview {
    ContentView()
}