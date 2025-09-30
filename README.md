# 聊天应用 (chatingAPP)

这是一个基于Web的聊天应用程序，包含用户管理、漂流瓶消息、私聊文本消息和私聊图片消息等功能。

## 项目结构

- `web_version_of_messages/`: 包含Web应用程序的核心代码。
  - `static/`: 静态资源文件，如CSS和图片。
    - `css/`: 样式表文件。
    - `images/`: 图片资源。
  - `templates/`: HTML模板文件。
- `chat.db`: SQLite3数据库文件（首次运行时自动创建）。
- `init_db.sql`: 数据库初始化脚本，用于创建数据库和表结构。

## 功能特性

- **用户管理**: 注册、登录，用户资料（名称、电话、性别、地点、密码）。
- **漂流瓶消息**: 用户可以发送和接收匿名消息。
- **私聊消息**: 用户之间可以进行一对一的文本聊天。
- **私聊图片消息**: 用户之间可以发送和接收图片（图片文件存储在文件系统中，数据库中仅存储路径）。

## 技术栈

- **后端**: Python (Flask)
- **前端**: HTML, CSS, JavaScript
- **数据库**: SQLite3

## 快速开始

### 1. 安装依赖

进入 `web_version_of_messages` 目录并安装依赖：

```bash
cd web_version_of_messages
pip install -r requirements.txt
```

或者使用 uv：

```bash
cd web_version_of_messages
uv pip install -r requirements.txt
```

### 2. 配置环境变量

1.  复制 `.env.example` 文件并重命名为 `.env`：

    ```bash
    cp .env.example .env
    ```

2.  编辑 `.env` 文件，设置应用配置：

    ```bash
    APP_IP=127.0.0.1
    APP_PORT=5000
    ```

### 3. 运行应用程序

在 `web_version_of_messages` 目录中运行：

```bash
python app.py
```

或者使用 uv：

```bash
uv run python app.py
```

首次运行时，应用会自动创建 `chat.db` 数据库文件并初始化表结构。

## 数据库结构概览

- `users`: 存储用户信息。
- `mm`: 存储漂流瓶消息。
- `private_text_messages`: 存储私聊文本消息。
- `private_image_messages`: 存储私聊图片消息（仅存储图片路径，图片文件保存在 `static/images/` 目录中）。

## 贡献

欢迎贡献！如果您有任何建议或改进，请随时提交 Pull Request。

## 许可证

(待补充，根据项目实际情况选择许可证)