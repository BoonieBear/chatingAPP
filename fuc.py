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
                       (name, msg, d.strftime("%Y-%m-%d %H:%M"), 0))
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
                       (sender_name, receiver_name, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:?"), 0))
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
                       (sender_name, receiver_name, image_data, image_type, image_size, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:?"), 0))
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
        
        # 获取所有相关的私聊消息，包括已读状态
        cursor.execute('''
            SELECT sender_name, receiver_name, message, send_time, is_read 
            FROM private_text_messages 
            WHERE (sender_name = ? AND receiver_name = ?) 
            OR (sender_name = ? AND receiver_name = ?)
            ORDER BY send_time ASC
        ''', (user_name, chat_with_name, chat_with_name, user_name))
        
        resultset = cursor.fetchall()
        
        # 标记为已读
        cursor.execute('''
            UPDATE private_text_messages 
            SET is_read = 1 
            WHERE receiver_name = ? AND sender_name = ?
        ''', (user_name, chat_with_name))
        
        conn.commit()
        conn.close()
        
        # 返回消息数据，包含已读状态
        return [(row['sender_name'], row['receiver_name'], row['message'], row['send_time'], row['is_read']) for row in resultset]
    except Exception as e:
        print(f"获取私聊消息时发生错误: {str(e)}")
        return []

# 获取与特定用户的私聊图片消息
def get_private_image_messages(user_name, chat_with_name):
    """获取与特定用户的私聊图片消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有相关的私聊图片消息，包括已读状态
        cursor.execute('''
            SELECT sender_name, receiver_name, image_data, image_type, image_size, send_time, is_read 
            FROM private_image_messages 
            WHERE (sender_name = ? AND receiver_name = ?) 
            OR (sender_name = ? AND receiver_name = ?)
            ORDER BY send_time ASC
        ''', (user_name, chat_with_name, chat_with_name, user_name))
        
        resultset = cursor.fetchall()
        
        # 标记为已读
        cursor.execute('''
            UPDATE private_image_messages 
            SET is_read = 1 
            WHERE receiver_name = ? AND sender_name = ?
        ''', (user_name, chat_with_name))
        
        conn.commit()
        conn.close()
        
        # 返回图片消息数据，包含已读状态
        return [(row['sender_name'], row['receiver_name'], row['image_data'], row['image_type'], row['image_size'], row['send_time'], row['is_read']) for row in resultset]
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
            (group_name, creator_name, d.strftime("%Y-%m-%d %H:%M:?"), description)
        )
        group_id = cursor.lastrowid
        
        # 将创建者添加为群组成员（管理员）
        cursor.execute(
            "INSERT INTO group_members(group_id, user_name, join_time, role) VALUES (?, ?, ?, ?)",
            (group_id, creator_name, d.strftime("%Y-%m-%d %H:%M:?"), "admin")
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
            (group_id, user_name, d.strftime("%Y-%m-%d %H:%M:?"))
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
            (group_id, sender_name, message, d.strftime("%Y-%m-%d %H:%M:?"))
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
            (user_name, content, ','.join(image_paths) if image_paths else None, d.strftime("%Y-%m-%d %H:%M:?"))
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
                           (moment_id, user_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:?")))
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
                      (moment_id, user_name, comment, d.strftime("%Y-%m-%d %H:%M:?")))
        
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