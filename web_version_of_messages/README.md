# 漂流瓶聊天程序 - 网页版

这是一个基于Flask的网页版漂流瓶聊天程序，具有用户注册登录、发送接收漂流瓶、私聊等功能。

## 功能特性

- 用户注册和登录
- 发送和接收漂流瓶消息
- 私聊功能
- 图片发送功能
- 消息已读未读状态显示
- 响应式网页设计

## 安装说明

### 环境要求

- Python 3.6+
- MySQL数据库

### 安装步骤

1. 克隆或下载本项目到本地

2. 进入项目目录
   ```
   cd web_version_of_messages
   ```

3. 创建虚拟环境（推荐）
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

4. 安装依赖
   ```
   pip install -r requirements.txt
   ```

5. 配置数据库连接
   打开 `../fuc.py` 文件，修改以下数据库连接信息：
   ```python
   connection = pymysql.connect(
       host='127.0.0.1',
       user='your_username',
       password='your_password',
       database='test_db',
       charset='utf8'
   )
   ```

6. 确保数据库表已创建
   执行 `../private_messages_table.sql` 和 `../img_Send.sql` 中的SQL语句创建必要的表。

## 运行程序

```
python app.py
```

程序将在 `http://localhost:5000` 上运行。

## 使用说明

1. 访问 `http://localhost:5000` 进入登录页面
2. 如果没有账号，点击"立即注册"创建新账号
3. 登录后可以：
   - 发送漂流瓶：点击"发送漂流瓶"按钮
   - 接收漂流瓶：点击"接收漂流瓶"按钮
   - 与好友私聊：在左侧聊天列表中选择用户开始聊天

## 目录结构

```
web_version_of_messages/
├── app.py                 # Flask主程序
├── requirements.txt       # 依赖包列表
├── README.md             # 说明文档
├── static/               # 静态文件目录
└── templates/            # HTML模板目录
    ├── base.html         # 基础模板
    ├── login.html        # 登录页面
    ├── register.html     # 注册页面
    ├── main.html         # 主页面
    └── about.html        # 关于页面
```

## 技术栈

- **后端**: Python, Flask, PyMySQL
- **前端**: HTML, CSS, JavaScript, Bootstrap 5, jQuery
- **数据库**: MySQL

## 版本信息

- **当前版本**: v2.0 网页版
- **原始版本**: v1.1 命令行版

## 许可证

© 2025 漂流瓶开发团队. 保留所有权利.