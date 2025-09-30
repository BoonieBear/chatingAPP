import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, QStackedWidget, 
                             QMessageBox, QGroupBox, QFormLayout, QSizePolicy, QDialog, 
                             QDialogButtonBox, QFrame, QListWidget, QListWidgetItem, QScrollArea,
                             QFileDialog, QAction, QMenuBar)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QFont, QPixmap, QIcon

import fuc
class Toast(QLabel):
    def __init__(self, text: str, parent: QWidget = None, duration: int = 2000):
        super().__init__(text, parent)

        self.duration = duration  # 显示毫秒
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)

        self.setFont(QFont("SimHei", 10))

    def show_message(self):
        # 调整大小以适应文本
        self.adjustSize()

        # 获取父窗口的几何区域（屏幕坐标）
        parent = self.parent()
        if parent:
            parent_rect = parent.rect()          # 父控件内部矩形
            parent_top_left = parent.mapToGlobal(QPoint(0, 0))  # 父控件在屏幕上的位置
            x = parent_top_left.x() + (parent_rect.width() - self.width()) // 2
            y = parent_top_left.y() + parent_rect.height() - self.height() - 20
        else:
            # 如果没有父控件，居中显示在屏幕
            screen_rect = QApplication.desktop().availableGeometry()
            x = (screen_rect.width() - self.width()) // 2
            y = screen_rect.height() - self.height() - 50

        self.move(x, y)
        self.show()

        # 自动隐藏
        QTimer.singleShot(self.duration, self.hide)
class LoginWidget(QWidget):
    login_successful = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.credentials_file = "user_credentials.txt"
        self.init_ui()
        self.load_credentials()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        # 标题
        title_label = QLabel("漂流瓶 v2.0")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            padding: 30px;
            background-color: rgba(25, 118, 210, 0.85);
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        """)
        
        # 登录表单容器
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        form_layout.addRow(QLabel("用户名:"), self.username_input)
        form_layout.addRow(QLabel("密码:"), self.password_input)
        
        form_container.setLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(25)
        
        self.login_btn = QPushButton("登录")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 120px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #1565c0;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        
        self.register_btn = QPushButton("注册")
        self.register_btn.setObjectName("register_btn")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 120px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #43a047;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        
        # 连接信号
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(form_container)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码")
            return
            
        try:
            # 模拟登录过程
            with fuc.connection.cursor() as cursor:
                sql = 'SELECT s_name,s_phone_num,s_sex,place,password FROM users WHERE s_name = ?'
                cursor.execute(sql, [username])
                resultset = cursor.fetchall()
                if len(resultset) == 0:
                    QMessageBox.warning(self, "错误", "用户不存在")
                else:
                    db_password = resultset[0][4]
                    if password == db_password:
                        toast = Toast("登录成功！", self)
                        toast.show_message()
                        # 保存凭证
                        self.save_credentials(username, password)
                        self.login_successful.emit(list(resultset[0]))
                    else:
                        QMessageBox.warning(self, "错误", "密码不正确！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录时发生错误: {str(e)}")
    
    def register(self):
        # 发送信号切换到注册界面
        self.login_successful.emit([])
        
    def save_credentials(self, username, password):
        """保存用户名和密码到本地文件"""
        try:
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                f.write(f"{username}\n{password}")
        except Exception as e:
            print(f"保存凭证时出错: {e}")
            
    def load_credentials(self):
        """从本地文件加载用户名和密码"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        username = lines[0].strip()
                        password = lines[1].strip()
                        self.username_input.setText(username)
                        self.password_input.setText(password)
        except Exception as e:
            print(f"加载凭证时出错: {e}")

class RegisterWidget(QWidget):
    register_successful = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        # 标题
        title_label = QLabel("用户注册")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            padding: 25px;
            background-color: rgba(76, 175, 80, 0.85);
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        """)
        
        # 注册表单容器
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入姓名")
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText("请输入密码")
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setMinimumHeight(40)
        self.reg_password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.reg_password_confirm_input = QLineEdit()
        self.reg_password_confirm_input.setPlaceholderText("请再次输入密码")
        self.reg_password_confirm_input.setEchoMode(QLineEdit.Password)
        self.reg_password_confirm_input.setMinimumHeight(40)
        self.reg_password_confirm_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入电话")
        self.phone_input.setMinimumHeight(40)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.place_input = QLineEdit()
        self.place_input.setPlaceholderText("请输入国家")
        self.place_input.setMinimumHeight(40)
        self.place_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.sex_input = QLineEdit()
        self.sex_input.setPlaceholderText("请输入性别(男/女)")
        self.sex_input.setMinimumHeight(40)
        self.sex_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 15px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        form_layout.addRow(QLabel("姓名:"), self.name_input)
        form_layout.addRow(QLabel("密码:"), self.reg_password_input)
        form_layout.addRow(QLabel("确认密码:"), self.reg_password_confirm_input)
        form_layout.addRow(QLabel("电话:"), self.phone_input)
        form_layout.addRow(QLabel("国家:"), self.place_input)
        form_layout.addRow(QLabel("性别:"), self.sex_input)
        
        form_container.setLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(25)
        
        self.submit_btn = QPushButton("提交")
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.setMinimumHeight(45)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 120px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #43a047;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        
        self.back_btn = QPushButton("返回")
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setMinimumHeight(45)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 120px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #e53935;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.back_btn)
        
        # 连接信号
        self.submit_btn.clicked.connect(self.register)
        self.back_btn.clicked.connect(self.back_to_login)
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(form_container)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def register(self):
        name = self.name_input.text().strip()
        password = self.reg_password_input.text().strip()
        password_confirm = self.reg_password_confirm_input.text().strip()
        phone = self.phone_input.text().strip()
        place = self.place_input.text().strip()
        sex = self.sex_input.text().strip()
        
        if not name or not password or not phone or not place or not sex:
            QMessageBox.warning(self, "警告", "请填写所有字段")
            return
            
        if password != password_confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
            
        try:
            with fuc.connection.cursor() as cursor:
                sql = 'INSERT INTO test_db.users(s_name,s_phone_num,s_sex,place,password) VALUES (%s,%s,%s,%s,%s)'
                cursor.execute(sql, [name, phone, sex, place, password])
                fuc.connection.commit()
                toast = Toast("注册成功！", self)
                toast.show_message()
                # 注册成功后发射信号
                user_info = [name, phone, sex, place, password]
                self.register_successful.emit(user_info)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注册时发生错误: {str(e)}")
            fuc.connection.rollback()
    
    def back_to_login(self):
        # 切换到登录界面的信号

        self.register_successful.emit([])

class ChatWidget(QWidget):
    def __init__(self, current_user, chat_with_user):
        super().__init__()
        self.current_user = current_user
        self.chat_with_user = chat_with_user
        self.message_count = 0  # 跟踪消息总数
        self.init_ui()
        self.load_messages()
        
        # 添加定时器用于自动刷新消息
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_messages)
        self.refresh_timer.start(3000)  # 每3秒刷新一次
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 聊天标题
        title_label = QLabel(f"与 {self.chat_with_user} 聊天")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #ffffff; 
            padding: 18px;
            background-color: rgba(25, 118, 210, 0.85);
            border-radius: 18px;
            margin-bottom: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        """)
        
        # 消息显示区域
        self.message_display = QTextEdit()
        self.message_display.setObjectName("message_display")
        self.message_display.setReadOnly(True)
        self.message_display.setMinimumHeight(400)
        self.message_display.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e1e1e1;
                border-radius: 18px;
                background-color: #ffffff;
                font-size: 15px;
                padding: 15px;
                selection-background-color: #3498db;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        
        # 消息输入区域
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 25px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(15)
        
        self.message_input = QLineEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setMinimumHeight(45)
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e1e1;
                border-radius: 22px;
                padding: 12px 20px;
                background-color: #f8f9fa;
                font-size: 15px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        # 发图按钮
        image_btn = QPushButton("⛶ 发图")
        image_btn.setObjectName("image_btn")
        image_btn.clicked.connect(self.send_image)
        image_btn.setMinimumHeight(45)
        image_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 70px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #43a047;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        
        send_btn = QPushButton("➤ 发送")
        send_btn.setObjectName("send_btn")
        send_btn.clicked.connect(self.send_message)
        send_btn.setMinimumHeight(45)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 10px 25px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 80px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #1565c0;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(image_btn)
        input_layout.addWidget(send_btn)
        input_container.setLayout(input_layout)
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.message_display)
        main_layout.addWidget(input_container)
        
        self.setLayout(main_layout)
        
    def load_messages(self, auto_scroll=True):
        # 获取文本消息和图片消息
        text_messages = fuc.get_private_messages(self.current_user[0], self.chat_with_user)
        image_messages = fuc.get_private_image_messages(self.current_user[0], self.chat_with_user)
        
        # 计算总消息数
        total_messages = len(text_messages) + len(image_messages)
        
        # 保存当前滚动位置
        scrollbar = self.message_display.verticalScrollBar()
        current_scroll_value = scrollbar.value()
        max_scroll_value = scrollbar.maximum()
        
        # 判断是否在底部（允许一些误差）
        at_bottom = (max_scroll_value - current_scroll_value) < 20
        

        
        # 构建完整的HTML内容
        html_content = """
        <style>
            .message-container {
                display: flex;
                flex-direction: column;
                padding: 15px;
                background-color: #ffffff;
            }
            .message-row {
                display: flex;
                margin: 15px 0;
                align-items: flex-end;
            }
            .message-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: #e0e0e0;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #666;
                font-weight: bold;
                font-size: 16px;
                margin: 0 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .message-content-container {
                display: flex;
                flex-direction: column;
                max-width: 70%;
            }
            .message-content {
                padding: 12px 20px;
                border-radius: 20px;
                position: relative;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                font-size: 15px;
                line-height: 1.5;
                word-wrap: break-word;
                margin: 0;
            }
            .sent .message-content {
                background-color: #1976d2;
                color: white;
                border-bottom-right-radius: 5px;
            }
            .received .message-content {
                background-color: #f0f0f0;
                color: #333;
                border-bottom-left-radius: 5px;
            }
            .message-info {
                display: flex;
                justify-content: flex-end;
                margin-top: 8px;
                font-size: 12px;
                color: #888;
            }
            .message-time {
                margin: 0 8px;
            }
            .message-status {
                font-size: 12px;
                color: #888;
            }
            .message-status.read {
                color: #4caf50;
            }
            .message-status.unread {
                color: #ff9800;
            }
            .image-message {
                max-width: 300px;
                border-radius: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                display: block;
                margin: 0;
                padding: 0;
                position: relative;
            }
            .image-container {
                margin: 0;
                padding: 0;
                line-height: 0;
                position: relative;
            }
            .image-wrapper {
                display: inline-block;
                margin: 0;
                padding: 0;
            }
        </style>
        <div class="message-container">
        """
        
        # 合并文本消息和图片消息
        all_messages = []
        
        # 添加文本消息
        for sender, receiver, message, time, is_read in text_messages:
            all_messages.append({
                'type': 'text',
                'sender': sender,
                'receiver': receiver,
                'content': message,
                'time': time,
                'is_read': is_read
            })
        
        # 添加图片消息
        for sender, receiver, image_data, image_type, time, is_read in image_messages:
            # 保存图片数据到文件
            image_path = fuc.save_image_data_to_file(image_data, image_type, sender, time)
            if image_path:
                all_messages.append({
                    'type': 'image',
                    'sender': sender,
                    'receiver': receiver,
                    'content': image_path,
                    'time': time,
                    'is_read': is_read
                })
        
        # 按时间排序（精确到秒）
        all_messages.sort(key=lambda x: x['time'])
        
        # 显示所有消息
        for msg in all_messages:
            # 获取用户首字母作为头像
            sender_initial = msg['sender'][0].upper() if msg['sender'] else "U"
            
            if msg['sender'] == self.current_user[0]:
                # 当前用户发送的消息 (右侧)
                status_text = "已读" if msg['is_read'] else "未读"
                status_class = "read" if msg['is_read'] else "unread"
                
                if msg['type'] == 'text':
                    html_content += f"""
                    <div class="message-row sent" style="justify-content: flex-end;">
                        <div class="message-content-container" style="text-align: right;">
                            <div class="message-content">{msg['content']}</div>
                            <div class="message-info">
                                <span class="message-time">{msg['time']}</span>
                                <span class="message-status {status_class}">{status_text}</span>
                            </div>
                        </div>
                    </div>
                    """
                else:  # 图片消息
                    html_content += f"""
                    <div class="message-row sent" style="justify-content: flex-end;">
                        <div class="message-content-container" style="text-align: right;">
                            <div class="message-content">

                                 <img src="{msg['content']}" class="image-message" alt="图片消息" onerror="this.style.display='none'; this.parentElement.innerHTML='<div>图片加载失败</div>';">
                                
                            </div>
                            <div class="message-info">
                                <span class="message-time">{msg['time']}</span>
                                <span class="message-status {status_class}">{status_text}</span>
                            </div>
                        </div>
                    </div>
                    """
            else:
                # 其他用户发送的消息 (左侧)
                if msg['type'] == 'text':
                    html_content += f"""
                    <div class="message-row received">
                        <div class="message-content-container" style="text-align: left;">
                            <div class="message-content">{msg['content']}</div>
                            <div class="message-info">
                                <span class="message-time">{msg['time']}</span>
                            </div>
                        </div>
                    </div>
                    """
                else:  # 图片消息
                    html_content += f"""
                    <div class="message-row received">
                        <div class="message-content-container" style="text-align: left;">
                            <div class="message-content">

                                <img src="{msg['content']}" class="image-message" alt="图片消息" onerror="this.style.display='none'; this.parentElement.innerHTML='<div>图片加载失败</div>';">
     
                            </div>
                            <div class="message-info">
                                <span class="message-time">{msg['time']}</span>
                            </div>
                        </div>
                    </div>
                    """
        
        html_content += "</div>"
        if(total_messages != self.message_count):
            self.message_display.setHtml(html_content)
            self.message_count = total_messages


    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return

        if fuc.send_private_message(self.current_user[0], self.chat_with_user, message):
            self.message_input.clear()
            # 发送消息时明确要求滚动到底部
            self.load_messages(auto_scroll=True)
            # 通知主窗口刷新聊天列表
            try:
                self.parent().parent().chat_list_widget.load_chat_list()
            except:
                pass
        else:
            QMessageBox.critical(self, "错误", "发送消息失败")
            
    def send_image(self):
        # 打开文件对话框选择图片
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择图片", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            # 创建图片存储目录
            import os
            image_dir = "images"
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            
            # 生成唯一的文件名
            import uuid
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{uuid.uuid4().hex}_{timestamp}{os.path.splitext(file_path)[1]}"
            destination_path = os.path.join(image_dir, unique_filename)
            
            # 复制图片到项目目录
            try:
                import shutil
                shutil.copy2(file_path, destination_path)
                
                # 保存图片消息到数据库
                if fuc.send_private_image_message(self.current_user[0], self.chat_with_user, destination_path):
                    # 发送图片时明确要求滚动到底部
                    self.load_messages(auto_scroll=True)
                    # 通知主窗口刷新聊天列表
                    try:
                        self.parent().parent().chat_list_widget.load_chat_list()
                    except:
                        pass
                else:
                    QMessageBox.critical(self, "错误", "发送图片消息失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"处理图片时发生错误: {str(e)}")
            
    def stop_refresh(self):
        """停止自动刷新"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
            
    def start_refresh(self):
        """开始自动刷新"""
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(3000)

class ChatListWidget(QWidget):
    chat_selected = pyqtSignal(str)
    
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()
        self.load_chat_list()
        
        # 添加定时器用于自动刷新
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_chat_list)
        self.refresh_timer.start(5000)  # 每5秒刷新一次
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel("聊天列表")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #ffffff; 
            padding: 15px;
            background-color: rgba(156, 39, 176, 0.85);
            border-radius: 15px;
            margin-bottom: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        """)
        
        # 聊天列表
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.on_chat_selected)
        self.chat_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e1e1e1;
                border-radius: 15px;
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 15px;
                padding: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 10px;
                margin: 5px 0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border-radius: 10px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        
        # 刷新按钮
        refresh_layout = QHBoxLayout()
        refresh_layout.setContentsMargins(0, 0, 0, 0)
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_btn.clicked.connect(self.load_chat_list)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #f57c00;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        
        refresh_label = QLabel("每5秒自动刷新")
        refresh_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            font-style: italic;
        """)
        
        refresh_layout.addWidget(self.refresh_btn)
        refresh_layout.addStretch()
        refresh_layout.addWidget(refresh_label)

        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.chat_list)
        main_layout.addLayout(refresh_layout)
        
        self.setLayout(main_layout)
        
    def load_chat_list(self):
        self.chat_list.clear()
        
        # 获取聊天用户列表
        chat_users = fuc.get_chat_users(self.current_user[0])
        
        # 获取有未读消息的用户（包括文本消息和图片消息）
        unread_text_users = fuc.get_unread_message_users(self.current_user[0])
        unread_image_users = fuc.get_unread_image_message_users(self.current_user[0])
        
        # 合并未读用户列表
        unread_users = set(unread_text_users + unread_image_users)
        
        # 添加所有聊天用户到列表
        for user in chat_users:
            item = QListWidgetItem(user)
            if user in unread_users:
                # 未读消息用户用粗体显示
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.chat_list.addItem(item)
            
        # 如果没有聊天记录，显示提示
        if not chat_users:
            item = QListWidgetItem("暂无聊天记录")
            item.setFlags(Qt.NoItemFlags)
            item.setToolTip("现在还没有好友哦，赶紧去添加一个吧！")
            self.chat_list.addItem(item)
        
    def on_chat_selected(self, item):
        if item.flags() != Qt.NoItemFlags:  # 不是提示项
            self.chat_selected.emit(item.text())
            
    def stop_refresh(self):
        """停止自动刷新"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
            
    def start_refresh(self):
        """开始自动刷新"""
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(5000)

class MainWidget(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 欢迎信息
        welcome_label = QLabel(f"欢迎, {self.user_info[0]}!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setObjectName("title_label")
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            padding: 25px;
            background-color: rgba(25, 118, 210, 0.85);
            border-radius: 20px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        """)
        
        # 用户信息卡片
        user_info_card = QFrame()
        user_info_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        user_info_layout = QHBoxLayout()
        user_info_layout.setSpacing(20)
        
        # 用户信息标签
        info_labels = [
            f"<b>用户名:</b> {self.user_info[0]}",
            f"<b>电话:</b> {self.user_info[1]}",
            f"<b>国家:</b> {self.user_info[3]}",
            f"<b>性别:</b> {self.user_info[2]}"
        ]
        
        for info in info_labels:
            label = QLabel(info)
            label.setStyleSheet("""
                color: #2c3e50;
                font-size: 14px;
                padding: 5px 10px;
            """)
            user_info_layout.addWidget(label)
        
        user_info_layout.addStretch()
        user_info_card.setLayout(user_info_layout)
        
        # 主要功能按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        self.send_btn = QPushButton("发送漂流瓶")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 180px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #1565c0;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        
        self.receive_btn = QPushButton("接收漂流瓶")
        self.receive_btn.setObjectName("receive_btn")
        self.receive_btn.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 180px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #8e24aa;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #7b1fa2;
            }
        """)
        
        self.exit_btn = QPushButton("退出登录")
        self.exit_btn.setObjectName("exit_btn")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                min-width: 180px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #e53935;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.receive_btn)
        button_layout.addWidget(self.exit_btn)
        
        # 聊天功能区域标题
        chat_title = QLabel("私聊消息")
        chat_title.setAlignment(Qt.AlignLeft)
        chat_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px 20px;
            background-color: rgba(156, 39, 176, 0.85);
            border-radius: 15px;
            margin-top: 10px;
        """)
        
        # 聊天功能区域
        chat_layout = QHBoxLayout()
        chat_layout.setSpacing(25)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        
        # 聊天列表
        self.chat_list_widget = ChatListWidget(self.user_info)
        self.chat_list_widget.chat_selected.connect(self.open_chat)
        self.chat_list_widget.setMaximumWidth(280)
        self.chat_list_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        
        # 聊天显示区域（初始为空）
        self.chat_display = QFrame()
        self.chat_display.setFrameStyle(QFrame.StyledPanel)
        self.chat_display.setMinimumHeight(450)
        self.chat_display.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        
        # 聊天提示标签
        self.chat_placeholder = QLabel("选择一个聊天或开始新聊天")
        self.chat_placeholder.setAlignment(Qt.AlignCenter)
        self.chat_placeholder.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 18px;
            font-weight: bold;
        """)
        
        # 将提示标签添加到聊天显示区域
        chat_display_layout = QVBoxLayout()
        chat_display_layout.addWidget(self.chat_placeholder)
        self.chat_display.setLayout(chat_display_layout)
        
        chat_layout.addWidget(self.chat_list_widget)
        chat_layout.addWidget(self.chat_display)
        
        # 连接信号
        self.send_btn.clicked.connect(self.send_message)
        self.receive_btn.clicked.connect(self.receive_message)
        self.exit_btn.clicked.connect(self.exit_app)
        
        # 添加到主布局
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(user_info_card)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(chat_title)
        main_layout.addLayout(chat_layout)
        
        # 添加一个占位符以填充空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(spacer)
        
        self.setLayout(main_layout)
        
    def send_message(self):
        dialog = SendMessageDialog(self.user_info[0], self)
        dialog.exec_()
        
    def receive_message(self):
        dialog = ReceiveMessageDialog(self)
        dialog.reply_requested.connect(self.open_chat_with_sender)
        dialog.exec_()
        
    def open_chat_with_sender(self, sender_name):
        """打开与漂流瓶发送者的聊天"""
        self.open_chat(sender_name)
        
        
    def exit_app(self):
        reply = QMessageBox.question(self, "确认", "确定要退出登录吗?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 停止聊天窗口的刷新定时器
            if hasattr(self, 'chat_widget') and self.chat_widget:
                self.chat_widget.stop_refresh()
            
            # 停止聊天列表的刷新定时器
            self.chat_list_widget.stop_refresh()
            
            # 返回到登录界面
            self.parent().parent().stacked_widget.setCurrentWidget(self.parent().parent().login_widget)
            
    def open_chat(self, chat_with_user):
        # 创建聊天窗口
        self.chat_widget = ChatWidget(self.user_info, chat_with_user)
        
        # 清空聊天显示区域并添加聊天窗口
        layout = self.chat_display.layout()
        if layout:
            # 清除现有内容
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout()
            self.chat_display.setLayout(layout)
            
        layout.addWidget(self.chat_widget)
        
        # 刷新聊天列表以更新未读状态
        self.chat_list_widget.load_chat_list()

class SendMessageDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("发送漂流瓶")
        self.setModal(True)
        self.resize(400, 250)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("请输入您的消息:")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        
        # 消息输入框
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("请输入消息（单行，最多100字）")
        self.msg_input.setMaximumHeight(100)
        
        # 添加选项：是否永久保存
        from PyQt5.QtWidgets import QCheckBox
        self.persist_checkbox = QCheckBox("永久保存漂流瓶（默认在回复时删除）")
        self.persist_checkbox.setChecked(False)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("发送")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        
        button_box.accepted.connect(self.send_message)
        button_box.rejected.connect(self.reject)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.msg_input)
        layout.addWidget(self.persist_checkbox)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def send_message(self):
        msg = self.msg_input.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "警告", "请输入消息内容")
            return
            
        if len(msg) > 100:
            QMessageBox.warning(self, "警告", "消息不能超过100字")
            return
            
        try:
            import datetime
            d = datetime.datetime.today()
            with fuc.connection.cursor() as cursor:
                # 检查是否需要永久保存
                is_persistent = 1 if self.persist_checkbox.isChecked() else 0
                # 在SQL中添加is_persistent字段，1表示永久保存，0表示可删除
                sql = 'INSERT INTO test_db.mm(name,msg,time,is_persistent) VALUES (%s,%s,%s,%s)'
                cursor.execute(sql, [self.username, msg, d.strftime("%Y-%m-%d %H:%M"), is_persistent])
                fuc.connection.commit()
                toast = Toast("发送成功", self)
                toast.show_message()
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发送消息时发生错误: {str(e)}")
            fuc.connection.rollback()

class ReceiveMessageDialog(QDialog):
    reply_requested = pyqtSignal(str)  # 发送者用户名
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sender_name = None
        self.init_ui()
        self.load_message()
        
    def init_ui(self):
        self.setWindowTitle("接收漂流瓶")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("您收到的漂流瓶:")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        
        # 消息显示区域
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.reply_btn = QPushButton("回复")
        self.reply_btn.setObjectName("reply_btn")
        self.reply_btn.clicked.connect(self.reply_message)
        
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("ok_btn")
        ok_btn.clicked.connect(self.accept_message)
        
        button_layout.addWidget(self.reply_btn)
        button_layout.addWidget(ok_btn)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.message_display)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_message(self):
        try:
            import random
            with fuc.connection.cursor() as cursor:
                # 只选择非永久保存的漂流瓶，或者添加一个机制来处理永久保存的漂流瓶
                sql = 'SELECT name,msg,time,is_persistent FROM mm WHERE TRUE'
                cursor.execute(sql, [])
                resultset = cursor.fetchall()
                l = len(resultset)
                if l <= 0:
                    self.message_display.setPlainText("没有捞到任何漂流瓶，请稍后再试...")
                    self.reply_btn.setEnabled(False)
                else:
                    pos = random.randint(0, l-1)
                    self.sender_name = resultset[pos][0]
                    name = resultset[pos][0]
                    msg = resultset[pos][1]
                    time = resultset[pos][2]
                    is_persistent = resultset[pos][3] if len(resultset[pos]) > 3 else 0
                    
                    # 获取用户信息
                    sql = 'SELECT s_name,s_phone_num,s_sex,place,password FROM users WHERE s_name = ?'
                    cursor.execute(sql, [name])
                    user_result = cursor.fetchall()
                    
                    if user_result:
                        user_info = user_result[0]
                        message_text = f"消息: {msg}\n\n来自: {name}\n时间: {time}\n电话: {user_info[1]}\n国家: {user_info[3]}\n性别: {user_info[2]}"
                    else:
                        message_text = f"消息: {msg}\n\n来自: {name}\n时间: {time}"
                    
                    self.message_display.setPlainText(message_text)
                    
                    # 保存漂流瓶信息，用于后续处理
                    self.current_bottle = {
                        'name': name,
                        'time': time,
                        'is_persistent': is_persistent
                    }
                    
                    # 如果是永久保存的漂流瓶，不自动删除
                    if is_persistent:
                        # 更新显示，提示用户这是永久保存的漂流瓶
                        current_text = self.message_display.toPlainText()
                        self.message_display.setPlainText(current_text + "\n\n[此漂流瓶已被发送者设置为永久保存]")
        except Exception as e:
            self.message_display.setPlainText(f"接收消息时发生错误: {str(e)}")
            self.reply_btn.setEnabled(False)
            
    def reply_message(self):
        if self.sender_name:
            # 如果不是永久保存的漂流瓶，则删除它
            if hasattr(self, 'current_bottle') and self.current_bottle.get('is_persistent', 0) == 0:
                try:
                    with fuc.connection.cursor() as cursor:
                        # 删除已读消息
                        sql = 'DELETE FROM mm WHERE time = %s and name = %s'
                        cursor.execute(sql, [self.current_bottle['time'], self.current_bottle['name']])
                        fuc.connection.commit()
                except Exception as e:
                    print(f"删除漂流瓶时出错: {e}")
            
            self.reply_requested.emit(self.sender_name)
            self.accept()
            
    def accept_message(self):
        # 如果不是永久保存的漂流瓶，则删除它
        if hasattr(self, 'current_bottle') and self.current_bottle.get('is_persistent', 0) == 0:
            try:
                with fuc.connection.cursor() as cursor:
                    # 删除已读消息
                    sql = 'DELETE FROM mm WHERE time = %s and name = %s'
                    cursor.execute(sql, [self.current_bottle['time'], self.current_bottle['name']])
                    fuc.connection.commit()
            except Exception as e:
                print(f"删除漂流瓶时出错: {e}")
        
        self.accept()

class DriftingBottleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_window")
        self.user_info = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("漂流瓶 v2.0")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 创建登录界面
        self.login_widget = LoginWidget()
        self.login_widget.login_successful.connect(self.on_login_successful)
        
        # 创建注册界面
        self.register_widget = RegisterWidget()
        self.register_widget.register_successful.connect(self.on_register_successful)
        
        # 添加到堆叠窗口
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        # 关于动作
        about_action = QAction('关于漂流瓶', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_about(self):
        """显示关于对话框"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def on_login_successful(self, user_info):
        if user_info == []:  # 切换到注册界面的信号
            self.stacked_widget.setCurrentWidget(self.register_widget)
        else:
            self.user_info = user_info
            # 创建主界面
            self.main_widget = MainWidget(user_info)
            self.stacked_widget.addWidget(self.main_widget)
            self.stacked_widget.setCurrentWidget(self.main_widget)
        
    def on_register_successful(self, user_info):
        if user_info is None:
            # 返回登录界面
            self.stacked_widget.setCurrentWidget(self.login_widget)
        elif user_info == []:
            # 切换到注册界面
            self.stacked_widget.setCurrentWidget(self.register_widget)
        else:
            # 注册成功，直接进入主界面
            self.user_info = user_info
            self.main_widget = MainWidget(user_info)
            self.stacked_widget.addWidget(self.main_widget)
            self.stacked_widget.setCurrentWidget(self.main_widget)
            
    def switch_to_register(self):
        self.stacked_widget.setCurrentWidget(self.register_widget)
        
    def switch_to_login(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)
        
    def open_chat_with_user(self, username):
        """打开与指定用户的聊天窗口"""
        if hasattr(self, 'main_widget') and self.main_widget:
            self.main_widget.open_chat(username)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("关于漂流瓶")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("漂流瓶 v2.0")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        
        # 版本信息
        version_label = QLabel("版本: 2.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 5px;
        """)
        
        # 描述信息
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setStyleSheet("""
            border: none;
            background-color: transparent;
            font-size: 14px;
            color: #34495e;
        """)
        desc_text.setText("""
<p>漂流瓶是一款基于Python和PyQt5开发的聊天应用程序。</p>

<p><b>主要功能：</b></p>
<ul>
<li>用户注册和登录</li>
<li>发送和接收漂流瓶消息</li>
<li>私聊功能</li>
<li>图片发送功能</li>
<li>消息已读未读状态显示</li>
</ul>

<p><b>技术栈：</b></p>
<ul>
<li>Python 3.x</li>
<li>PyQt5</li>
<li>MySQL数据库</li>
</ul>

<p><b>版本历史：</b></p>
<ul>
<li>v1.1 - 基础命令行版本</li>
<li>v2.0 - 图形界面版本，新增私聊和图片功能</li>
</ul>

<p>© 2025 漂流瓶开发团队. 保留所有权利.</p>
        """)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(desc_text)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 应用QSS样式表
    try:
        with open("styles.qss", "r", encoding="utf-8") as f:
            style_sheet = f.read()
            app.setStyleSheet(style_sheet)
    except FileNotFoundError:
        print("未找到样式表文件 styles.qss")
    
    window = DriftingBottleApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()