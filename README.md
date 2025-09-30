# 聊天应用 (chatingAPP)

这是一个基于Web的聊天应用程序，包含用户管理、漂流瓶消息、私聊文本消息和私聊图片消息等功能。

## 项目结构

- `web_version_of_messages/`: 包含Web应用程序的核心代码。
  - `static/`: 静态资源文件，如CSS和图片。
    - `css/`: 样式表文件。
    - `images/`: 图片资源。
  - `templates/`: HTML模板文件。
- `init_db.sql`: 数据库初始化脚本，用于创建数据库和表结构。

## 功能特性

- **用户管理**: 注册、登录，用户资料（名称、电话、性别、地点、密码）。
- **漂流瓶消息**: 用户可以发送和接收匿名消息。
- **私聊消息**: 用户之间可以进行一对一的文本聊天。
- **私聊图片消息**: 用户之间可以发送和接收图片。

## 技术栈 (推测)

- **后端**: Python (可能使用 Flask 或 Django)
- **前端**: HTML, CSS, JavaScript
- **数据库**: MySQL

## 快速开始

### 1. 配置环境变量

1.  复制 `.env.example` 文件并重命名为 `.env`：

    ```bash
    cp .env.example .env
    ```

2.  编辑 `.env` 文件，根据您的数据库和应用设置更新以下变量：

    ```
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=your_database_password
    DB_NAME=test_db

    APP_IP=127.0.0.1
    APP_PORT=5000
    ```

### 2. 数据库设置

1.  确保您已安装 MySQL 数据库。
2.  使用提供的 `init_db.sql` 脚本初始化数据库。

    ```bash
    mysql -u $DB_USER -p$DB_PASSWORD < init_db.sql
    ```

    或者，如果您在 `.env` 中设置了 `DB_USER` 和 `DB_PASSWORD`，可以使用：

    ```bash
    mysql -u $(grep DB_USER .env | cut -d '=' -f2) -p$(grep DB_PASSWORD .env | cut -d '=' -f2) < init_db.sql
    ```

    请注意，上述命令仅为示例，实际操作中请根据您的shell环境和安全实践进行调整。

### 3. 运行应用程序 (待补充)

具体的运行步骤将取决于后端框架的选择。通常包括：

1.  安装项目依赖。
2.  配置数据库连接（通常会从 `.env` 文件读取）。
3.  启动Web服务器。

## 数据库结构概览

- `users`: 存储用户信息。
- `mm`: 存储漂流瓶消息。
- `private_messages`: 存储私聊文本消息。
- `private_image_messages`: 存储私聊图片消息。

## 贡献

欢迎贡献！如果您有任何建议或改进，请随时提交 Pull Request。

## 许可证

(待补充，根据项目实际情况选择许可证)