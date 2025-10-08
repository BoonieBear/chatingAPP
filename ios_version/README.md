# 漂流瓶聊天 iOS 应用

这是一个使用 SwiftUI 开发的 iOS 版漂流瓶聊天应用，采用 iOS 18 风格设计，通过 GET/POST 请求与 Flask 后端进行通信。

## 功能特性

- ✅ 用户登录和注册
- ✅ 私聊功能（文本消息）
- ✅ 朋友圈功能（发布、点赞、评论）
- ✅ 个人资料管理
- ✅ 文件分享功能
- ✅ iOS 18 风格界面设计

## 项目结构

```
ChatApp/
├── ChatApp/
│   ├── App/
│   │   ├── AppDelegate.swift
│   │   ├── SceneDelegate.swift
│   │   └── ContentView.swift
│   ├── Services/
│   │   └── NetworkManager.swift
│   ├── Views/
│   │   ├── LoginView.swift
│   │   ├── ChatListView.swift
│   │   ├── ChatView.swift
│   │   ├── MomentsView.swift
│   │   ├── ProfileView.swift
│   │   └── FileShareView.swift
│   └── Assets.xcassets/
└── ChatApp.xcodeproj/
```

## 系统要求

- iOS 18.0+
- Xcode 15.0+
- Swift 5.9+

## 安装与运行

1. 克隆或下载项目到本地
2. 打开 `ChatApp.xcodeproj` 文件
3. 确保你的开发设备或模拟器运行 iOS 18.0 或更高版本
4. 修改 `NetworkManager.swift` 中的 `baseURL` 为你的服务器地址
5. 点击运行按钮或使用快捷键 `Cmd+R` 运行应用

## 配置说明

### 服务器地址

在 `NetworkManager.swift` 文件中修改以下行：

```swift
private let baseURL = "http://127.0.0.1:5000"
```

将其改为你的 Flask 服务器地址。

### 网络权限

应用需要访问网络，已在 `Info.plist` 中配置了必要的网络权限：

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

## 主要功能说明

### 登录与注册

- 支持用户名和密码登录
- 注册需要填写用户名、密码、手机号、所在地和性别
- 登录状态会保存在本地，下次打开应用自动登录

### 聊天功能

- 显示聊天用户列表
- 支持发送文本消息
- 支持发送文件（图片、文档等）
- 消息按时间排序显示

### 朋友圈功能

- 查看朋友圈动态
- 发布朋友圈（支持文字和图片）
- 点赞和评论功能
- 图片选择和上传

### 个人资料

- 查看和编辑个人资料
- 更换头像
- 设置主题偏好（浅色/深色/跟随系统）
- 通知设置

### 文件分享

- 支持多种文件类型
- 文件预览和下载
- 文件大小显示

## 技术特点

- 使用 SwiftUI 构建用户界面
- 采用 MVVM 架构模式
- 使用 async/await 处理异步网络请求
- 支持 iOS 18 的新特性和设计风格
- 响应式布局，适配不同屏幕尺寸

## 注意事项

1. 确保后端 Flask 服务正在运行
2. 网络连接正常，可以访问服务器
3. 服务器地址配置正确
4. 如果遇到大文件下载问题，确保服务器使用 `send_from_directory` 函数

## 开发者

使用 Swift 和 SwiftUI 开发，采用 iOS 18 设计规范，提供现代化的用户体验。