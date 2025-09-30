import random
from dotenv import load_dotenv # 导入 load_dotenv

# 代码文件：code/chapter7/fuc.py
#  查询数据实现

import pymysql
import os
import datetime

load_dotenv() # 加载 .env 文件中的环境变量

"""todo:
设置地址，密码，数据库名
"""
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8'
)
def roll():
    connection.rollback()


# 1. 建立数据库连接
def login():




        # 2. 创建游标对象
    with connection.cursor() as cursor:
        # 准备SQL语句
        os.system("cls")
        ch=input("\n<登录> \n\t【1】注册 【2】登录\n")
        if ch=='1':
            name=input("请输入姓名")
            password=input("请输入密码")
            password_2=input("请输入再次输入密码")
            if password != password_2:
                print("不一致！！！")
                exit(0)
            phone=input("请输入电话")
            place=input("请输入国家")
            sex=input("请输入性别(男/女)")
            sql='INSERT INTO test_db.users(s_name,s_phone_num,s_sex,place,password) VALUES (%s,%s,%s,%s,%s)'
            cursor.execute(sql, [name, phone, sex, place,password])
            connection.commit()
            print("注册成功！")
            os.system("pause")
            return [name, phone, sex, place,password]
        else:
            sql = 'SELECT s_name,s_phone_num,s_sex,place,password FROM users WHERE s_name = %s'
            cursor.execute(sql, [input("请输入用户名")])
            resultset = cursor.fetchall()
            if len(resultset) == 0:
                print("用户不存在")
                os.system("pause")
                exit(0)
            else:
                password = resultset[0][4]
                ppp=input("请输入ta的密码:")
                if password == ppp:
                    print("登录成功！")
                    os.system("pause")
                    return resultset[0]
                else:
                    print("密码不正确！")
                    os.system("pause")
                    exit(0)






    # 捕获数据库异常


def sent(name):
    os.system("cls")
    print("<发送>")
    sql='INSERT INTO test_db.mm(name,msg,time) VALUES (%s,%s,%s)'
    msg=input("请输入消息（单行，最多100字，附件自带信息）")
    d=datetime.datetime.today()
    with connection.cursor() as cursor:
        cursor.execute(sql, [name,msg,d.strftime("%Y-%m-%d %H:%M")])
        connection.commit()
        print("发送成功！")
        os.system("pause")

def get_a_msg():
    os.system("cls")
    print("<接收信息>")
    sql = 'SELECT name,msg,time FROM mm WHERE TRUE'
    with connection.cursor() as cursor:
        cursor.execute(sql,[])
        resultset = cursor.fetchall()
        l=len(resultset)
        if l<=0 :
            print("没有信息")
            os.system("pause")
            return
        pos=random.randint(0,l-1)
        name = resultset[pos][0]
        msg = resultset[pos][1]
        time = resultset[pos][2]
        print("消息:")
        print(msg)
        sql = 'SELECT s_name,s_phone_num,s_sex,place,password FROM users WHERE s_name = %s'
        cursor.execute(sql,[name])
        resultset = cursor.fetchall()
        print("--来自于%s,时间%s,电话%s,国家%s,性别%s"%(name,time,resultset[0][1],resultset[0][3],resultset[0][2]))
        sql = 'DELETE FROM mm WHERE time = %s and name = %s'
        cursor.execute(sql,[time,name])
        connection.commit()
        os.system("pause")

# 发送私聊消息
def send_private_message(sender_name, receiver_name, message):
    try:
        d = datetime.datetime.today()
        with connection.cursor() as cursor:
            sql = 'INSERT INTO test_db.private_text_messages(sender_name, receiver_name, message, send_time) VALUES (%s,%s,%s,%s)'
            cursor.execute(sql, [sender_name, receiver_name, message, d.strftime("%Y-%m-%d %H:%M:%S")])
            connection.commit()
            return True
    except Exception as e:
        print(f"发送私聊消息时发生错误: {str(e)}")
        connection.rollback()
        return False

# 发送私聊图片消息
def send_private_image_message(sender_name, receiver_name, image_path):
    try:
        # 读取图片文件的二进制数据
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 获取图片类型
        import os
        image_type = os.path.splitext(image_path)[1][1:]  # 去掉点号
        
        # 将二进制数据转换为base64编码
        import base64
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        
        d = datetime.datetime.today()
        with connection.cursor() as cursor:
            sql = 'INSERT INTO test_db.private_image_messages(sender_name, receiver, image_data, image_type, send_time) VALUES (%s,%s,%s,%s,%s)'
            cursor.execute(sql, [sender_name, receiver_name, image_data_base64, image_type, d.strftime("%Y-%m-%d %H:%M:%S")])
            connection.commit()
            return True
    except Exception as e:
        print(f"发送私聊图片消息时发生错误: {str(e)}")
        connection.rollback()
        return False

# 获取与特定用户的私聊消息
def get_private_messages(user_name, chat_with_name):
    try:
        with connection.cursor() as cursor:
            # 获取所有相关的私聊消息，包括已读状态
            sql = '''SELECT sender_name, receiver_name, message, send_time, is_read 
                     FROM private_text_messages 
                     WHERE (sender_name = %s AND receiver_name = %s) 
                     OR (sender_name = %s AND receiver_name = %s)
                     ORDER BY send_time ASC'''
            cursor.execute(sql, [user_name, chat_with_name, chat_with_name, user_name])
            resultset = cursor.fetchall()
            
            # 标记为已读
            sql = '''UPDATE private_text_messages 
                     SET is_read = TRUE 
                     WHERE receiver_name = %s AND sender_name = %s'''
            cursor.execute(sql, [user_name, chat_with_name])
            connection.commit()
            
            # 返回消息数据，包含已读状态
            return [ (row[0], row[1], row[2], row[3], row[4])for row in resultset ]
    except Exception as e:
        print(f"获取私聊消息时发生错误: {str(e)}")
        return []

# 获取与特定用户的私聊图片消息
def get_private_image_messages(user_name, chat_with_name):
    try:
        with connection.cursor() as cursor:
            # 获取所有相关的私聊图片消息，包括已读状态
            sql = '''SELECT sender_name, receiver, image_data, image_type, send_time, is_read 
                     FROM private_image_messages 
                     WHERE (sender_name = %s AND receiver = %s) 
                     OR (sender_name = %s AND receiver = %s)
                     ORDER BY send_time ASC'''
            cursor.execute(sql, [user_name, chat_with_name, chat_with_name, user_name])
            resultset = cursor.fetchall()
            
            # 标记为已读
            sql = '''UPDATE private_image_messages 
                     SET is_read = TRUE 
                     WHERE receiver = %s AND sender_name = %s'''
            cursor.execute(sql, [user_name, chat_with_name])
            connection.commit()
            
            # 返回图片消息数据，包含已读状态
            # 注意：这里仍然返回sender_name和receiver_name，以保持与代码其他部分的一致性
            return [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in resultset]
    except Exception as e:
        print(f"获取私聊图片消息时发生错误: {str(e)}")
        return []

# 获取有未读消息的用户列表
def get_unread_message_users(user_name):
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT DISTINCT sender_name 
                     FROM private_text_messages 
                     WHERE receiver_name = %s AND is_read = FALSE'''
            cursor.execute(sql, [user_name])
            resultset = cursor.fetchall()
            return [row[0] for row in resultset]
    except Exception as e:
        print(f"获取未读消息用户时发生错误: {str(e)}")
        return []

# 获取有未读图片消息的用户列表
def get_unread_image_message_users(user_name):
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT DISTINCT sender_name 
                     FROM private_image_messages 
                     WHERE receiver = %s AND is_read = FALSE'''
            cursor.execute(sql, [user_name])
            resultset = cursor.fetchall()
            return [row[0] for row in resultset]
    except Exception as e:
        print(f"获取未读图片消息用户时发生错误: {str(e)}")
        return []

# 获取所有与当前用户有过私聊的用户列表
def get_chat_users(user_name):
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT DISTINCT sender_name 
                     FROM private_text_messages 
                     WHERE receiver_name = %s AND sender_name != %s
                     UNION
                     SELECT DISTINCT receiver_name 
                     FROM private_text_messages 
                     WHERE sender_name = %s AND receiver_name != %s
                     UNION
                     SELECT DISTINCT sender_name 
                     FROM private_image_messages 
                     WHERE receiver = %s AND sender_name != %s
                     UNION
                     SELECT DISTINCT receiver 
                     FROM private_image_messages 
                     WHERE sender_name = %s AND receiver != %s'''
            cursor.execute(sql, [user_name, user_name, user_name, user_name, user_name, user_name, user_name, user_name])
            resultset = cursor.fetchall()
            # 注意：这里仍然返回sender_name和receiver_name，以保持与代码其他部分的一致性
            return [row[0] for row in resultset if row[0] != user_name]
    except Exception as e:
        print(f"获取聊天用户时发生错误: {str(e)}")
        return []

# 保存图片数据到本地文件并返回文件路径
def save_image_data_to_file(image_data, image_type, sender_name, send_time):
    try:
        # 创建图片存储目录
        import os
        image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_version_of_messages", "static", "images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        # 生成安全的文件名（使用UUID避免编码问题）
        import uuid
        import re
        # 清理发送者名称中的非法字符
        clean_sender_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', sender_name)
        # 使用UUID和当前时间戳生成唯一文件名，避免时间格式问题
        import time
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{clean_sender_name}_{timestamp}_{unique_id}.{image_type}"
        file_path = os.path.join(image_dir, filename)
        
        # 检查image_data是否为base64字符串
        if isinstance(image_data, str):
            # 解码base64数据
            import base64
            image_data_binary = base64.b64decode(image_data)
        else:
            # 如果已经是二进制数据，直接使用
            image_data_binary = image_data
        
        # 写入图片数据
        with open(file_path, 'wb') as f:
            f.write(image_data_binary)
        
        # 返回相对于web_version_of_messages/static目录的路径
        return os.path.join("images", filename)
    except Exception as e:
        print(f"保存图片数据时发生错误: {str(e)}")
        return None
