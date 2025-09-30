from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
import sys
import os
from dotenv import load_dotenv # 导入 load_dotenv

# 将上级目录添加到Python路径中，以便导入fuc模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fuc
import datetime
import base64

load_dotenv() # 加载 .env 文件中的环境变量

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 在生产环境中应该使用更安全的密钥
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 静态文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, filename)

# 首页路由
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('main'))
    return redirect(url_for('login'))

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with fuc.connection.cursor() as cursor:
                sql = 'SELECT s_name,s_phone_num,s_sex,place,password FROM users WHERE s_name = %s'
                cursor.execute(sql, [username])
                resultset = cursor.fetchall()
                if len(resultset) == 0:
                    flash('用户不存在', 'error')
                else:
                    db_password = resultset[0][4]
                    if password == db_password:
                        session['username'] = username
                        session['user_info'] = {
                            'name': resultset[0][0],
                            'phone': resultset[0][1],
                            'sex': resultset[0][2],
                            'place': resultset[0][3]
                        }
                        return redirect(url_for('main'))
                    else:
                        flash('密码不正确！', 'error')
        except Exception as e:
            flash(f'登录时发生错误: {str(e)}', 'error')
    
    return render_template('login.html')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        phone = request.form['phone']
        place = request.form['place']
        sex = request.form['sex']
        
        if not name or not password or not phone or not place or not sex:
            flash('请填写所有字段', 'error')
            return render_template('register.html')
            
        if password != password_confirm:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
            
        try:
            with fuc.connection.cursor() as cursor:
                sql = 'INSERT INTO test_db.users(s_name,s_phone_num,s_sex,place,password) VALUES (%s,%s,%s,%s,%s)'
                cursor.execute(sql, [name, phone, sex, place, password])
                fuc.connection.commit()
                flash('注册成功！', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f'注册时发生错误: {str(e)}', 'error')
            fuc.connection.rollback()
    
    return render_template('register.html')

# 主页面
@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_info = session['user_info']
    return render_template('main.html', user_info=user_info)

# 发送漂流瓶
@app.route('/send_bottle', methods=['POST'])
def send_bottle():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    msg = request.form['message']
    is_persistent = request.form.get('is_persistent', '0')
    
    if not msg:
        return jsonify({'success': False, 'message': '请输入消息内容'})
        
    if len(msg) > 100:
        return jsonify({'success': False, 'message': '消息不能超过100字'})
    
    try:
        d = datetime.datetime.today()
        with fuc.connection.cursor() as cursor:
            sql = 'INSERT INTO test_db.mm(name,msg,time,is_persistent) VALUES (%s,%s,%s,%s)'
            cursor.execute(sql, [session['username'], msg, d.strftime("%Y-%m-%d %H:%M:%S"), is_persistent])
            fuc.connection.commit()
            return jsonify({'success': True, 'message': '发送成功'})
    except Exception as e:
        fuc.connection.rollback()
        return jsonify({'success': False, 'message': f'发送消息时发生错误: {str(e)}'})

# 接收漂流瓶
@app.route('/receive_bottle')
def receive_bottle():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    try:
        with fuc.connection.cursor() as cursor:
            sql = 'SELECT name,msg,time,is_persistent FROM mm WHERE TRUE'
            cursor.execute(sql, [])
            resultset = cursor.fetchall()
            l = len(resultset)
            if l <= 0:
                return jsonify({'success': True, 'message': '没有捞到任何漂流瓶，请稍后再试...', 'data': None})
            else:
                import random
                pos = random.randint(0, l-1)
                sender_name = resultset[pos][0]
                msg = resultset[pos][1]
                time = resultset[pos][2]
                is_persistent = resultset[pos][3] if len(resultset[pos]) > 3 else 0
                
                # 获取用户信息
                sql = 'SELECT s_name,s_phone_num,s_sex,place,password FROM users WHERE s_name = %s'
                cursor.execute(sql, [sender_name])
                user_result = cursor.fetchall()
                
                if user_result:
                    user_info = {
                        'name': user_result[0][0],
                        'phone': user_result[0][1],
                        'sex': user_result[0][2],
                        'place': user_result[0][3]
                    }
                else:
                    user_info = None
                
                # 注意：与GUI版本不同，Web版本不在这里删除漂流瓶
                # 而是在用户明确选择回复时才删除（如果是非永久的）
                
                return jsonify({
                    'success': True,
                    'data': {
                        'message': msg,
                        'sender': sender_name,
                        'time': time,
                        'is_persistent': is_persistent,
                        'sender_info': user_info
                    }
                })
    except Exception as e:
        return jsonify({'success': False, 'message': f'接收消息时发生错误: {str(e)}'})

# 回复漂流瓶
@app.route('/reply_bottle', methods=['POST'])
def reply_bottle():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    try:
        data = request.get_json()
        sender_name = data.get('sender_name')
        bottle_time = data.get('time')
        is_persistent = data.get('is_persistent', 0)
        
        if not sender_name or not bottle_time:
            return jsonify({'success': False, 'message': '缺少必要参数'})
        
        # 如果不是永久保存的漂流瓶，则删除它
        if is_persistent == 0:
            with fuc.connection.cursor() as cursor:
                sql = 'DELETE FROM mm WHERE time = %s and name = %s'
                cursor.execute(sql, [bottle_time, sender_name])
                fuc.connection.commit()
        
        # 返回成功，前端将打开与发送者的聊天
        return jsonify({
            'success': True, 
            'message': '删除成功，准备打开聊天窗口',
            'chat_with': sender_name
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'回复漂流瓶时发生错误: {str(e)}'})

# 获取聊天用户列表
@app.route('/chat_users')
def chat_users():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    try:
        chat_users = fuc.get_chat_users(session['username'])
        unread_text_users = fuc.get_unread_message_users(session['username'])
        unread_image_users = fuc.get_unread_image_message_users(session['username'])
        
        # 合并未读用户列表
        unread_users = set(unread_text_users + unread_image_users)
        
        # 构造返回数据
        users_data = []
        for user in chat_users:
            users_data.append({
                'name': user,
                'has_unread': user in unread_users
            })
        
        return jsonify({'success': True, 'data': users_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取聊天用户时发生错误: {str(e)}'})

# 获取与特定用户的聊天记录
@app.route('/chat_messages/<chat_with_user>')
def chat_messages(chat_with_user):
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    try:
        # 获取文本消息和图片消息
        text_messages = fuc.get_private_messages(session['username'], chat_with_user)
        image_messages = fuc.get_private_image_messages(session['username'], chat_with_user)
        
        # 合并消息
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
            try:
                # 保存图片数据到文件并获取路径
                image_path = fuc.save_image_data_to_file(image_data, image_type, sender, time)
                if image_path:
                    # 生成图片的URL，相对于static目录
                    # 移除"images/"前缀，因为static目录会自动映射
                    if image_path.startswith("images/"):
                        image_url = "/static/" + image_path
                    else:
                        image_url = "/static/images/" + os.path.basename(image_path)
                    all_messages.append({
                        'type': 'image',
                        'sender': sender,
                        'receiver': receiver,
                        'content': image_url,
                        'time': time,
                        'is_read': is_read
                    })
            except Exception as e:
                print(f"处理图片消息时发生错误: {str(e)}")
                # 即使单个图片消息处理失败，也不影响其他消息
                continue
        
        # 按时间排序
        all_messages.sort(key=lambda x: x['time'])
        
        return jsonify({'success': True, 'data': all_messages})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取聊天消息时发生错误: {str(e)}'})

# 发送私聊消息
@app.route('/send_private_message', methods=['POST'])
def send_private_message():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    receiver_name = request.form['receiver']
    message = request.form['message']
    
    if not receiver_name or not message:
        return jsonify({'success': False, 'message': '接收者和消息内容不能为空'})
    
    try:
        if fuc.send_private_message(session['username'], receiver_name, message):
            return jsonify({'success': True, 'message': '发送成功'})
        else:
            return jsonify({'success': False, 'message': '发送失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送消息时发生错误: {str(e)}'})

# 发送私聊图片消息
@app.route('/send_private_image', methods=['POST'])
def send_private_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    receiver_name = request.form['receiver']
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '没有上传图片'})
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'success': False, 'message': '没有选择图片'})
    destination_path = None # 初始化 destination_path
    try:
        # 创建图片存储目录
        image_dir = os.path.join(app.root_path, 'static', 'images')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        # 生成唯一的文件名
        import uuid
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{uuid.uuid4().hex}_{timestamp}{os.path.splitext(image_file.filename)[1]}"
        destination_path = os.path.join(image_dir, unique_filename)
        
        # 保存图片到static/images目录
        image_file.save(destination_path)
        
        # 保存图片消息到数据库
        full_image_path = os.path.join('images', unique_filename)
        if fuc.send_private_image_message(session['username'], receiver_name, destination_path):
            return jsonify({'success': True, 'message': '发送成功'})
        else:
            # 如果保存数据库失败，删除已保存的图片文件
            if destination_path and os.path.exists(destination_path): # 检查 destination_path 是否已赋值
                os.remove(destination_path)
            return jsonify({'success': False, 'message': '发送失败'})
    except Exception as e:
        # 删除可能已保存的图片文件
        if destination_path and os.path.exists(destination_path): # 检查 destination_path 是否已赋值
            os.remove(destination_path)
        return jsonify({'success': False, 'message': f'发送图片时发生错误: {str(e)}'})

# 退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 关于页面
@app.route('/about')
def about():
    return render_template('about.html')

# 下载程序页面
@app.route('/download')
def download():
    return render_template('download.html')

# 下载程序文件
@app.route('/download_program')
def download_program():
    import os
    import zipfile
    from flask import send_file
    
    # 创建临时zip文件在static目录下
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    zip_filename = 'drifting_bottle_v2.0.zip'
    zip_path = os.path.join(static_dir, zip_filename)
    
    # 如果zip文件已存在且不是太旧，则直接返回
    if os.path.exists(zip_path):
        import time
        # 如果文件小于1小时，直接返回
        if time.time() - os.path.getmtime(zip_path) < 3600:
            return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    
    # 创建zip文件
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # 添加主要程序文件
        main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for root, dirs, files in os.walk(main_dir):
            # 跳过 __pycache__ 和 .git 目录，以及web_version_of_messages的static目录
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
            
            for file in files:
                if not file.endswith('.pyc'):  # 跳过编译文件
                    file_path = os.path.join(root, file)
                    # 跳过web_version_of_messages/static目录下的zip文件
                    if 'web_version_of_messages' in file_path and 'static' in file_path and file.endswith('.zip'):
                        continue
                    arc_path = os.path.relpath(file_path, main_dir)
                    zipf.write(file_path, arc_path)
    
    return send_file(zip_path, as_attachment=True, download_name=zip_filename)

if __name__ == '__main__':
    APP_IP = os.getenv('APP_IP', '127.0.0.1')  # 默认值
    APP_PORT = int(os.getenv('APP_PORT', 5000)) # 默认值
    app.run(debug=True, host=APP_IP, port=APP_PORT)