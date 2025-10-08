import random
import os
import datetime
import base64
import sqlite3

# SQLite数据库配置
DATABASE = '/Users/fusean/code/FYH/chatingAPP/chat.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问数据
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            s_name TEXT NOT NULL UNIQUE,
            s_phone_num TEXT,
            s_sex TEXT,
            place TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 创建漂流瓶消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            msg TEXT NOT NULL,
            time TEXT NOT NULL,
            is_persistent INTEGER DEFAULT 0
        )
    ''')
    
    # 创建私聊文本消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_text_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT NOT NULL,
            receiver_name TEXT NOT NULL,
            message TEXT NOT NULL,
            send_time TEXT NOT NULL,
            is_read INTEGER DEFAULT 0
        )
    ''')
    
    # 创建私聊图片消息表
    cursor.execute("DROP TABLE IF EXISTS private_image_messages")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_image_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT NOT NULL,
            receiver_name TEXT NOT NULL,
            image_data BLOB,
            image_type TEXT,
            image_size INTEGER,
            send_time TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (sender_name) REFERENCES users(s_name),
            FOREIGN KEY (receiver_name) REFERENCES users(s_name)
        )
    ''')
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_sender ON private_image_messages(sender_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_receiver ON private_image_messages(receiver_name)")
    
    # 创建群组表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL UNIQUE,
            creator_name TEXT NOT NULL,
            create_time TEXT NOT NULL,
            FOREIGN KEY (creator_name) REFERENCES users(s_name)
        )
    ''')
    
    # 创建群成员表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            member_name TEXT NOT NULL,
            join_time TEXT NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (member_name) REFERENCES users(s_name)
        )
    ''')
    
    # 创建群消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            sender_name TEXT NOT NULL,
            message TEXT NOT NULL,
            send_time TEXT NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (sender_name) REFERENCES users(s_name)
        )
    ''')
    
    # 创建朋友圈表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT NOT NULL,
            content TEXT NOT NULL,
            image_data BLOB,
            image_type TEXT,
            image_size INTEGER,
            send_time TEXT NOT NULL,
            FOREIGN KEY (sender_name) REFERENCES users(s_name)
        )
    ''')
    
    # 创建朋友圈评论表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moment_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moment_id INTEGER NOT NULL,
            sender_name TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            send_time TEXT NOT NULL,
            FOREIGN KEY (moment_id) REFERENCES moments(id),
            FOREIGN KEY (sender_name) REFERENCES users(s_name)
        )
    ''')
    
    # 创建朋友圈点赞表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moment_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moment_id INTEGER NOT NULL,
            sender_name TEXT NOT NULL,
            send_time TEXT NOT NULL,
            FOREIGN KEY (moment_id) REFERENCES moments(id),
            FOREIGN KEY (sender_name) REFERENCES users(s_name)
        )
    ''')
    
    conn.commit()
    conn.close()

def roll():
    """回滚事务"""
    pass  # SQLite在连接关闭时会自动回滚未提交的事务

# 用户登录/注册功能
def login():
    """用户登录/注册"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    os.system("cls" if os.name == "nt" else "clear")
    ch = input("\n<登录> \n\t【1】注册 【2】登录\n")
    
    if ch == '1':
        name = input("请输入姓名: ")
        password = input("请输入密码: ")
        password_2 = input("请再次输入密码: ")
        
        if password != password_2:
            print("密码不一致！！！")
            input("按回车键继续...")
            return None
            
        phone = input("请输入电话: ")
        place = input("请输入国家: ")
        sex = input("请输入性别(男/女): ")
        
        try:
            cursor.execute(
                "INSERT INTO users(s_name, s_phone_num, s_sex, place, password) VALUES (?, ?, ?, ?, ?)",
                (name, phone, sex, place, password)
            )
            conn.commit()
            print("注册成功！")
            input("按回车键继续...")
            conn.close()
            return [name, phone, sex, place, password]
        except sqlite3.IntegrityError:
            print("用户名已存在！")
            input("按回车键继续...")
            conn.close()
            return None
        except Exception as e:
            print(f"注册时发生错误: {str(e)}")
            input("按回车键继续...")
            conn.close()
            return None
    else:
        username = input("请输入用户名: ")
        cursor.execute("SELECT s_name, s_phone_num, s_sex, place, password FROM users WHERE s_name = ?", (username,))
        result = cursor.fetchone()
        
        if result is None:
            print("用户不存在")
            input("按回车键继续...")
            conn.close()
            return None
        else:
            password = result['password']
            ppp = input("请输入密码: ")
            if password == ppp:
                print("登录成功")
                input("按回车键继续...")
                conn.close()
                return result
            else:
                print("密码错误")
                input("按回车键继续...")
                conn.close()
                return None

def sent(name):
    """发送漂流瓶消息"""
    os.system("cls" if os.name == "nt" else "clear")
    print("<发送>")
    msg = input("请输入消息（单行，最多100字，附件自带信息）: ")
    d = datetime.datetime.today()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mm(name, msg, time, is_persistent) VALUES (?, ?, ?, ?)",
                       (name, msg, d.strftime("%Y-%m-%d %H:%M:%S"), 0))
        conn.commit()
        print("发送成功！")
    except Exception as e:
        print(f"发送失败: {str(e)}")
    finally:
        conn.close()
    input("按回车键继续...")

def get_a_msg(name):
    """获取一个漂流瓶消息"""
    os.system("cls" if os.name == "nt" else "clear")
    print("<接收信息>")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 随机获取一个未被当前用户发送的漂流瓶
    cursor.execute("SELECT name, msg, time FROM mm WHERE name != ? ORDER BY RANDOM() LIMIT 1", (name,))
    result = cursor.fetchone()
    
    if result:
        print("\n<接收到漂流瓶>\n")
        print(f"来自: {result['name']}")
        print(f"内容: {result['msg']}")
        print(f"时间: {result['time']}")
        
        # 将该漂流瓶标记为已读（如果需要，或者删除）
        # 这里我们选择删除，因为漂流瓶通常是一次性的
        cursor.execute("DELETE FROM mm WHERE time = ? AND name = ?", (result['time'], result['name']))
        conn.commit()
    else:
        print("\n没有漂流瓶了，去扔一个吧！")
    
    conn.close()
    input("按回车键继续...")

def get_a_msg(name):
    """获取一个漂流瓶消息"""
    os.system("cls" if os.name == "nt" else "clear")
    print("<接收信息>")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, msg, time FROM mm")
    resultset = cursor.fetchall()
    
    if len(resultset) <= 0:
        print("没有信息")
        input("按回车键继续...")
        conn.close()
        return
    
    pos = random.randint(0, len(resultset) - 1)
    name = resultset[pos]['name']
    msg = resultset[pos]['msg']
    time = resultset[pos]['time']
    
    print("消息:")
    print(msg)
    
    cursor.execute("SELECT s_name, s_phone_num, s_sex, place, password FROM users WHERE s_name = ?", (name,))
    user_result = cursor.fetchone()
    
    if user_result:
        print(f"--来自于{name},时间{time},电话{user_result['s_phone_num']},国家{user_result['place']},性别{user_result['s_sex']}")
    
    cursor.execute("DELETE FROM mm WHERE time = ? AND name = ?", (time, name))
    conn.commit()
    conn.close()
    
    input("按回车键继续...")

# 发送私聊消息
def send_private_message(sender_name, receiver_name, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO private_text_messages(sender_name, receiver_name, message, send_time, is_read) VALUES (?, ?, ?, ?, ?)",
                       (sender_name, receiver_name, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0))
        conn.commit()
        return True
    except Exception as e:
        print(f"发送私聊文本消息失败: {str(e)}")
        return False
    finally:
        conn.close()

def get_private_messages(user1, user2):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM private_text_messages WHERE (sender_name = ? AND receiver_name = ?) OR (sender_name = ? AND receiver_name = ?) ORDER BY send_time",
                   (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()
    return messages

# 发送私聊图片消息
def send_private_image_message(sender_name, receiver_name, image_data, image_type, image_size):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO private_image_messages(sender_name, receiver_name, image_data, image_type, image_size, send_time, is_read) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (sender_name, receiver_name, image_data, image_type, image_size, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0))
        conn.commit()
        return True
    except Exception as e:
        print(f"发送私聊图片消息失败: {str(e)}")
        return False
    finally:
        conn.close()

def get_private_image_messages(user1, user2):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM private_image_messages WHERE (sender_name = ? AND receiver_name = ?) OR (sender_name = ? AND receiver_name = ?) ORDER BY send_time",
                   (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()
    return messages

# 获取与特定用户的私聊消息
def get_private_messages(user_name, chat_with_name):
    """获取与特定用户的私聊文本消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有相关的私聊消息，包括已读状态和撤回状态
        cursor.execute('''
            SELECT id, sender_name, receiver_name, message, send_time, is_read, is_withdrawn 
            FROM private_text_messages 
            WHERE (sender_name = ? AND receiver_name = ?) 
            OR (sender_name = ? AND receiver_name = ?)
            ORDER BY send_time ASC
        ''', (user_name, chat_with_name, chat_with_name, user_name))
        
        resultset = cursor.fetchall()
        
        # 标记为已读（仅对未撤回的消息）
        cursor.execute('''
            UPDATE private_text_messages 
            SET is_read = 1 
            WHERE receiver_name = ? AND sender_name = ? AND is_withdrawn = 0
        ''', (user_name, chat_with_name))
        
        conn.commit()
        conn.close()
        
        # 返回消息数据，包含已读状态和撤回状态
        return [(row['id'], row['sender_name'], row['receiver_name'], row['message'], row['send_time'], row['is_read'], bool(row['is_withdrawn'])) for row in resultset]
    except Exception as e:
        print(f"获取私聊消息时发生错误: {str(e)}")
        return []

# 获取与特定用户的私聊图片消息
def get_private_image_messages(user_name, chat_with_name):
    """获取与特定用户的私聊图片消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有相关的私聊图片消息，包括已读状态和撤回状态
        cursor.execute('''
            SELECT id, sender_name, receiver_name, image_data, image_type, image_size, send_time, is_read, is_withdrawn 
            FROM private_image_messages 
            WHERE (sender_name = ? AND receiver_name = ?) 
            OR (sender_name = ? AND receiver_name = ?)
            ORDER BY send_time ASC
        ''', (user_name, chat_with_name, chat_with_name, user_name))
        
        resultset = cursor.fetchall()
        
        # 标记为已读（仅对未撤回的消息）
        cursor.execute('''
            UPDATE private_image_messages 
            SET is_read = 1 
            WHERE receiver_name = ? AND sender_name = ? AND is_withdrawn = 0
        ''', (user_name, chat_with_name))
        
        conn.commit()
        conn.close()
        
        # 返回图片消息数据，包含已读状态和撤回状态
        return [(row['id'], row['sender_name'], row['receiver_name'], row['image_data'], row['image_type'], row['image_size'], row['send_time'], row['is_read'], bool(row['is_withdrawn'])) for row in resultset]
    except Exception as e:
        print(f"获取私聊图片消息时发生错误: {str(e)}")
        return []

# 获取有未读消息的用户列表
def get_unread_message_users(user_name):
    """获取有未读文本消息的用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT sender_name 
            FROM private_text_messages 
            WHERE receiver_name = ? AND is_read = 0
        ''', (user_name,))
        
        resultset = cursor.fetchall()
        conn.close()
        return [row['sender_name'] for row in resultset]
    except Exception as e:
        print(f"获取未读消息用户时发生错误: {str(e)}")
        return []

# 获取有未读图片消息的用户列表
def get_unread_image_message_users(user_name):
    """获取有未读图片消息的用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT sender_name 
            FROM private_image_messages 
            WHERE receiver_name = ? AND is_read = 0
        ''', (user_name,))
        
        resultset = cursor.fetchall()
        conn.close()
        return [row['sender_name'] for row in resultset]
    except Exception as e:
        print(f"获取未读图片消息用户时发生错误: {str(e)}")
        return []

# 获取所有与当前用户有过私聊的用户列表
def get_chat_users(user_name):
    """获取所有与当前用户有过私聊的用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT sender_name 
            FROM private_text_messages 
            WHERE receiver_name = ? AND sender_name != ?
            UNION
            SELECT DISTINCT receiver_name 
            FROM private_text_messages 
            WHERE sender_name = ? AND receiver_name != ?
            UNION
            SELECT DISTINCT sender_name 
            FROM private_image_messages 
            WHERE receiver_name = ? AND sender_name != ?
            UNION
            SELECT DISTINCT receiver_name 
            FROM private_image_messages 
            WHERE sender_name = ? AND receiver_name != ?
        ''', (user_name, user_name, user_name, user_name, user_name, user_name, user_name, user_name))
        
        resultset = cursor.fetchall()
        conn.close()
        return [row['sender_name'] for row in resultset if row['sender_name'] != user_name]
    except Exception as e:
        print(f"获取聊天用户时发生错误: {str(e)}")
        return []

# 保存图片数据到本地文件并返回文件路径
def save_image_data_to_file(image_data, image_type, sender_name, send_time):
    """保存图片数据到本地文件并返回文件路径"""
    try:
        # 创建图片存储目录
        image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_version_of_messages", "static", "images")
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        # 检查image_data是否为base64字符串
        if isinstance(image_data, str):
            # 解码base64数据
            image_data_binary = base64.b64decode(image_data)
        else:
            # 如果已经是二进制数据，直接使用
            image_data_binary = image_data
        
        # 使用图片内容的哈希值作为文件名，避免重复保存
        import hashlib
        image_hash = hashlib.sha256(image_data_binary).hexdigest()
        filename = f"{image_hash}.{image_type}"
        file_path = os.path.join(image_dir, filename)
        
        # 如果文件已存在，则直接返回其路径，不再重复写入
        if os.path.exists(file_path):
            return os.path.join("images", filename)

        # 写入图片数据
        with open(file_path, 'wb') as f:
            f.write(image_data_binary)
        
        # 返回相对于web_version_of_messages/static目录的路径
        return os.path.join("images", filename)
    except Exception as e:
        print(f"保存图片数据时发生错误: {str(e)}")
        return None

# 群组相关函数
def create_group(creator_name, group_name, description=""):
    """创建群组"""
    try:
        d = datetime.datetime.today()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建群组
        cursor.execute(
            "INSERT INTO groups(name, creator, created_time, description) VALUES (?, ?, ?, ?)",
            (group_name, creator_name, d.strftime("%Y-%m-%d %H:%M:%S"), description)
        )
        group_id = cursor.lastrowid
        
        # 将创建者添加为群组成员（管理员）
        cursor.execute(
            "INSERT INTO group_members(group_id, user_name, join_time, role) VALUES (?, ?, ?, ?)",
            (group_id, creator_name, d.strftime("%Y-%m-%d %H:%M:%S"), "admin")
        )
        conn.commit()
        conn.close()
        return group_id
    except Exception as e:
        print(f"创建群组失败: {str(e)}")
        return None

def add_group_member(group_id, user_name):
    """添加群组成员"""
    try:
        d = datetime.datetime.today()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否已经是群组成员
        cursor.execute(
            "SELECT id FROM group_members WHERE group_id = ? AND user_name = ?",
            (group_id, user_name)
        )
        if cursor.fetchone():
            conn.close()
            return True  # 用户已经是成员
        
        # 添加用户为群组成员
        cursor.execute(
            "INSERT INTO group_members(group_id, user_name, join_time) VALUES (?, ?, ?)",
            (group_id, user_name, d.strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"添加群组成员失败: {str(e)}")
        return False

def get_user_groups(user_name):
    """获取用户所属的群组列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT g.id, g.name, g.creator, g.created_time, g.description
            FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_name = ?
            ORDER BY g.created_time DESC
        ''', (user_name,))
        
        resultset = cursor.fetchall()
        conn.close()
        
        groups = []
        for row in resultset:
            groups.append({
                'id': row['id'],
                'name': row['name'],
                'creator': row['creator'],
                'created_time': row['created_time'],
                'description': row['description']
            })
        
        return groups
    except Exception as e:
        print(f"获取用户群组时发生错误: {str(e)}")
        return []

def get_group_members(group_id):
    """获取群组成员列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_name, join_time, role
            FROM group_members
            WHERE group_id = ?
            ORDER BY join_time ASC
        ''', (group_id,))
        
        resultset = cursor.fetchall()
        conn.close()
        
        members = []
        for row in resultset:
            members.append({
                'user_name': row['user_name'],
                'join_time': row['join_time'],
                'role': row['role']
            })
        
        return members
    except Exception as e:
        print(f"获取群组成员时发生错误: {str(e)}")
        return []

def send_group_message(group_id, sender_name, message):
    """发送群组消息"""
    try:
        d = datetime.datetime.today()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO group_messages(group_id, sender_name, message, send_time) VALUES (?, ?, ?, ?)",
            (group_id, sender_name, message, d.strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"发送群组消息失败: {str(e)}")
        return False

def get_group_messages(group_id):
    """获取群组消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sender_name, message, send_time
            FROM group_messages
            WHERE group_id = ?
            ORDER BY send_time ASC
        ''', (group_id,))
        
        resultset = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in resultset:
            messages.append({
                'sender_name': row['sender_name'],
                'message': row['message'],
                'send_time': row['send_time']
            })
        
        return messages
    except Exception as e:
        print(f"获取群组消息时发生错误: {str(e)}")
        return []

# 朋友圈相关功能函数

def create_moment(user_name, content, image_paths):
    """创建朋友圈"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        d = datetime.datetime.today()
        cursor.execute(
            "INSERT INTO moments(user_name, content, image_paths, post_time) VALUES (?, ?, ?, ?)",
            (user_name, content, ','.join(image_paths) if image_paths else None, d.strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"创建朋友圈时发生错误: {str(e)}")
        return False

def get_moments():
    """获取所有朋友圈"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有朋友圈，按时间倒序排列
        cursor.execute("""
            SELECT m.id, m.user_name, m.content, m.image_paths, m.post_time, u.s_phone_num, u.s_sex, u.place
            FROM moments m
            JOIN users u ON m.user_name = u.s_name
            ORDER BY m.post_time DESC
            LIMIT 50
        """)
        
        moments_data = []
        for row in cursor.fetchall():
            # 获取评论
            cursor.execute("""
                SELECT mc.user_name, mc.comment, mc.comment_time, u.s_phone_num, u.s_sex, u.place
                FROM moment_comments mc
                JOIN users u ON mc.user_name = u.s_name
                WHERE mc.moment_id = ?
                ORDER BY mc.comment_time ASC
            """, (row[0],))
            
            comments = []
            for comment_row in cursor.fetchall():
                comments.append({
                    'user_name': comment_row[0],
                    'comment': comment_row[1],
                    'comment_time': comment_row[2],
                    'user_info': {
                        'phone': comment_row[3],
                        'sex': comment_row[4],
                        'place': comment_row[5]
                    }
                })
            
            # 获取点赞数
            cursor.execute("SELECT COUNT(*) FROM moment_likes WHERE moment_id = ?", (row[0],))
            like_count = cursor.fetchone()['COUNT(*)']
            
            # 处理图片路径
            image_path = row[3]  # image_paths字段现在是单个路径而不是数组
            
            moments_data.append({
                'id': row[0],
                'user_name': row[1],
                'content': row[2],
                'image_paths': image_path,  # 使用单个路径而不是数组
                'post_time': row[4],
                'user_info': {
                    'phone': row[5],
                    'sex': row[6],
                    'place': row[7]
                },
                'comments': comments,
                'like_count': like_count
            })
        
        conn.close()
        return moments_data
    except Exception as e:
        print(f"获取朋友圈时发生错误: {str(e)}")
        return []

def like_moment(moment_id, user_name):
    """点赞朋友圈"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已经点赞
        cursor.execute("SELECT id FROM moment_likes WHERE moment_id = ? AND user_name = ?", (moment_id, user_name))
        existing_like = cursor.fetchone()
        
        if existing_like:
            # 如果已点赞，则取消点赞
            cursor.execute("DELETE FROM moment_likes WHERE moment_id = ? AND user_name = ?", (moment_id, user_name))
            conn.commit()
            conn.close()
            return False  # 表示取消点赞
        else:
            # 如果未点赞，则添加点赞
            cursor.execute("INSERT INTO moment_likes(moment_id, user_name, like_time) VALUES (?, ?, ?)",
                           (moment_id, user_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            return True  # 表示点赞成功
    except Exception as e:
        print(f"点赞/取消点赞朋友圈失败: {str(e)}")
        return False

def comment_moment(moment_id, user_name, comment):
    """评论朋友圈"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 添加评论
        d = datetime.datetime.today()
        cursor.execute("INSERT INTO moment_comments(moment_id, user_name, comment, comment_time) VALUES (?, ?, ?, ?)", 
                      (moment_id, user_name, comment, d.strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"评论朋友圈失败: {str(e)}")
        return False

# 初始化数据库
init_db()

def get_unread_messages_count(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM private_text_messages WHERE receiver_name = ? AND is_read = 0", (username,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_unread_image_messages_count(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM private_image_messages WHERE receiver_name = ? AND is_read = 0", (username,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# 用户在线状态相关函数
def update_user_status(user_name, is_online):
    """更新用户在线状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户状态记录是否存在
        cursor.execute("SELECT id FROM user_status WHERE user_name = ?", (user_name,))
        result = cursor.fetchone()
        
        if result:
            # 更新现有记录
            cursor.execute(
                "UPDATE user_status SET is_online = ?, last_seen = ? WHERE user_name = ?",
                (is_online, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_name)
            )
        else:
            # 创建新记录
            cursor.execute(
                "INSERT INTO user_status(user_name, is_online, last_seen) VALUES (?, ?, ?)",
                (user_name, is_online, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"更新用户状态失败: {str(e)}")
        return False

def get_user_status(user_name):
    """获取用户在线状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_online, last_seen FROM user_status WHERE user_name = ?", (user_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'is_online': bool(result['is_online']),
                'last_seen': result['last_seen']
            }
        else:
            return {
                'is_online': False,
                'last_seen': None
            }
    except Exception as e:
        print(f"获取用户状态失败: {str(e)}")
        return {
            'is_online': False,
            'last_seen': None
        }

def get_online_users():
    """获取所有在线用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_name FROM user_status WHERE is_online = 1")
        resultset = cursor.fetchall()
        conn.close()
        return [row['user_name'] for row in resultset]
    except Exception as e:
        print(f"获取在线用户失败: {str(e)}")
        return []


def get_user_notifications(user_name, limit=20):
    """获取用户通知"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM notifications WHERE user_name = ? ORDER BY created_at DESC LIMIT ?",
            (user_name, limit)
        )
        resultset = cursor.fetchall()
        conn.close()
        
        notifications = []
        for row in resultset:
            notifications.append({
                'id': row['id'],
                'type': row['type'],
                'title': row['title'],
                'content': row['content'],
                'is_read': bool(row['is_read']),
                'created_at': row['created_at']
            })
        
        return notifications
    except Exception as e:
        print(f"获取用户通知失败: {str(e)}")
        return []

def mark_notification_as_read(notification_id):
    """标记通知为已读"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"标记通知为已读失败: {str(e)}")
        return False

def get_unread_notifications_count(user_name):
    """获取未读通知数量"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_name = ? AND is_read = 0", (user_name,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"获取未读通知数量失败: {str(e)}")
        return 0

# 个人资料相关函数
def create_or_update_user_profile(user_name, avatar_path=None, bio=None, birth_date=None, theme_preference='light', notification_enabled=True):
    """创建或更新用户个人资料"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户资料是否存在
        cursor.execute("SELECT id FROM user_profiles WHERE user_name = ?", (user_name,))
        result = cursor.fetchone()
        
        if result:
            # 更新现有资料
            update_fields = []
            params = []
            
            if avatar_path is not None:
                update_fields.append("avatar_path = ?")
                params.append(avatar_path)
            
            if bio is not None:
                update_fields.append("bio = ?")
                params.append(bio)
            
            if birth_date is not None:
                update_fields.append("birth_date = ?")
                params.append(birth_date)
            
            if theme_preference is not None:
                update_fields.append("theme_preference = ?")
                params.append(theme_preference)
            
            if notification_enabled is not None:
                update_fields.append("notification_enabled = ?")
                params.append(notification_enabled)
            
            if update_fields:
                params.append(user_name)
                query = f"UPDATE user_profiles SET {', '.join(update_fields)} WHERE user_name = ?"
                cursor.execute(query, params)
        else:
            # 创建新资料
            cursor.execute(
                "INSERT INTO user_profiles(user_name, avatar_path, bio, birth_date, theme_preference, notification_enabled) VALUES (?, ?, ?, ?, ?, ?)",
                (user_name, avatar_path, bio, birth_date, theme_preference, notification_enabled)
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"创建或更新用户资料失败: {str(e)}")
        return False

def get_user_profile(user_name):
    """获取用户个人资料"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_name = ?", (user_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_name': result['user_name'],
                'avatar_path': result['avatar_path'],
                'bio': result['bio'],
                'birth_date': result['birth_date'],
                'theme_preference': result['theme_preference'],
                'notification_enabled': bool(result['notification_enabled'])
            }
        else:
            return {
                'user_name': user_name,
                'avatar_path': None,
                'bio': None,
                'birth_date': None,
                'theme_preference': 'light',
                'notification_enabled': True
            }
    except Exception as e:
        print(f"获取用户资料失败: {str(e)}")
        return None

# 文件分享相关函数
def save_shared_file(sender_name, receiver_name, file_name, file_path, file_size, file_type):
    """保存分享的文件信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO shared_files(sender_name, receiver_name, file_name, file_path, file_size, file_type, send_time, is_read) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (sender_name, receiver_name, file_name, file_path, file_size, file_type, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
        )
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    except Exception as e:
        print(f"保存分享文件失败: {str(e)}")
        return None

def get_shared_files(user_name, with_user=None):
    """获取分享的文件"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if with_user:
            # 获取与特定用户的文件分享记录
            cursor.execute(
                "SELECT * FROM shared_files WHERE (sender_name = ? AND receiver_name = ?) OR (sender_name = ? AND receiver_name = ?) ORDER BY send_time DESC",
                (user_name, with_user, with_user, user_name)
            )
        else:
            # 获取用户所有的文件分享记录
            cursor.execute(
                "SELECT * FROM shared_files WHERE sender_name = ? OR receiver_name = ? ORDER BY send_time DESC",
                (user_name, user_name)
            )
        
        resultset = cursor.fetchall()
        conn.close()
        
        files = []
        for row in resultset:
            files.append({
                'id': row['id'],
                'sender_name': row['sender_name'],
                'receiver_name': row['receiver_name'],
                'file_name': row['file_name'],
                'file_path': row['file_path'], # 添加 file_path
                'file_size': row['file_size'],
                'file_type': row['file_type'],
                'send_time': row['send_time'],
                'is_read': bool(row['is_read'])
            })
        
        return files
    except Exception as e:
        print(f"获取分享文件失败: {str(e)}")
        return []

def mark_file_as_read(file_id):
    """标记文件为已读"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE shared_files SET is_read = 1 WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"标记文件为已读失败: {str(e)}")
        return False

# 消息撤回相关函数
def withdraw_text_message(message_id, sender_name):
    """撤回文本消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证消息是否属于发送者
        cursor.execute("SELECT sender_name FROM private_text_messages WHERE id = ?", (message_id,))
        result = cursor.fetchone()
        
        if not result or result['sender_name'] != sender_name:
            conn.close()
            return False
        
        # 标记消息为已撤回
        cursor.execute(
            "UPDATE private_text_messages SET is_withdrawn = 1, withdrawn_time = ? WHERE id = ?",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message_id)
        )
        
        # 记录撤回操作
        cursor.execute(
            "INSERT INTO message_withdrawals(message_id, message_type, sender_name, withdrawn_time) VALUES (?, 'text', ?, ?)",
            (message_id, sender_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"撤回文本消息失败: {str(e)}")
        return False

def withdraw_image_message(message_id, sender_name):
    """撤回图片消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证消息是否属于发送者
        cursor.execute("SELECT sender_name FROM private_image_messages WHERE id = ?", (message_id,))
        result = cursor.fetchone()
        
        if not result or result['sender_name'] != sender_name:
            conn.close()
            return False
        
        # 标记消息为已撤回
        cursor.execute(
            "UPDATE private_image_messages SET is_withdrawn = 1, withdrawn_time = ? WHERE id = ?",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message_id)
        )
        
        # 记录撤回操作
        cursor.execute(
            "INSERT INTO message_withdrawals(message_id, message_type, sender_name, withdrawn_time) VALUES (?, 'image', ?, ?)",
            (message_id, sender_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"撤回图片消息失败: {str(e)}")
        return False

def is_message_withdrawn(message_id, message_type):
    """检查消息是否已被撤回"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if message_type == 'text':
            cursor.execute("SELECT is_withdrawn FROM private_text_messages WHERE id = ?", (message_id,))
        elif message_type == 'image':
            cursor.execute("SELECT is_withdrawn FROM private_image_messages WHERE id = ?", (message_id,))
        else:
            conn.close()
            return False
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return bool(result['is_withdrawn'])
        else:
            return False
    except Exception as e:
        print(f"检查消息撤回状态失败: {str(e)}")
        return False

# 更新数据库结构
def update_database():
    """更新数据库结构以支持新功能"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 添加用户在线状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE,
                is_online INTEGER DEFAULT 0,
                last_seen TEXT,
                FOREIGN KEY (user_name) REFERENCES users(s_name)
            )
        ''')
        
        # 添加用户通知表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_name) REFERENCES users(s_name)
            )
        ''')
        
        # 添加用户个人资料扩展表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE,
                avatar_path TEXT,
                bio TEXT,
                birth_date TEXT,
                theme_preference TEXT DEFAULT 'light',
                notification_enabled INTEGER DEFAULT 1,
                FOREIGN KEY (user_name) REFERENCES users(s_name)
            )
        ''')
        
        # 添加文件分享表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_name TEXT NOT NULL,
                receiver_name TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                send_time TEXT DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY (sender_name) REFERENCES users(s_name),
                FOREIGN KEY (receiver_name) REFERENCES users(s_name)
            )
        ''')
        
        # 检查是否需要添加撤回相关字段
        cursor.execute("PRAGMA table_info(private_text_messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_withdrawn' not in columns:
            cursor.execute("ALTER TABLE private_text_messages ADD COLUMN is_withdrawn INTEGER DEFAULT 0")
        
        if 'withdrawn_time' not in columns:
            cursor.execute("ALTER TABLE private_text_messages ADD COLUMN withdrawn_time TEXT")
        
        cursor.execute("PRAGMA table_info(private_image_messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_withdrawn' not in columns:
            cursor.execute("ALTER TABLE private_image_messages ADD COLUMN is_withdrawn INTEGER DEFAULT 0")
        
        if 'withdrawn_time' not in columns:
            cursor.execute("ALTER TABLE private_image_messages ADD COLUMN withdrawn_time TEXT")
        
        # 添加撤回通知表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                sender_name TEXT NOT NULL,
                withdrawn_time TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_name) REFERENCES users(s_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"更新数据库结构失败: {str(e)}")
        return False

# 执行数据库更新
update_database()