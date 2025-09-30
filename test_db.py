#!/usr/bin/env python3
# 测试脚本，用于验证MySQL数据库和基本功能

import sys
import os

# 将上级目录添加到Python路径中，以便导入fuc模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fuc

def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        conn = fuc.get_db_connection()
        print("✓ 数据库连接成功")
        conn.close()
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False
    return True

def test_database_tables():
    """测试数据库表创建"""
    print("测试数据库表创建...")
    try:
        conn = fuc.get_db_connection()
        cursor = conn.cursor()
        
        # 检查表是否存在
        tables = ['users', 'mm', 'private_text_messages', 'private_image_messages']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                print(f"✓ 表 {table} 存在")
            else:
                print(f"✗ 表 {table} 不存在")
                conn.close()
                return False
        
        conn.close()
        print("✓ 所有表都已正确创建")
    except Exception as e:
        print(f"✗ 数据库表检查失败: {e}")
        return False
    return True

def test_user_registration():
    """测试用户注册"""
    print("测试用户注册...")
    try:
        conn = fuc.get_db_connection()
        cursor = conn.cursor()
        
        # 插入测试用户
        cursor.execute(
            "INSERT OR IGNORE INTO users(s_name, s_phone_num, s_sex, place, password) VALUES (?, ?, ?, ?, ?)",
            ("testuser", "1234567890", "男", "中国", "testpass")
        )
        conn.commit()
        
        # 验证用户是否插入成功
        cursor.execute("SELECT s_name FROM users WHERE s_name = ?", ("testuser",))
        if cursor.fetchone():
            print("✓ 用户注册成功")
        else:
            print("✗ 用户注册失败")
            conn.close()
            return False
        
        # 清理测试用户
        cursor.execute("DELETE FROM users WHERE s_name = ?", ("testuser",))
        conn.commit()
        conn.close()
        print("✓ 测试用户已清理")
    except Exception as e:
        print(f"✗ 用户注册测试失败: {e}")
        return False
    return True

def test_message_sending():
    """测试消息发送"""
    print("测试消息发送...")
    try:
        conn = fuc.get_db_connection()
        cursor = conn.cursor()
        
        # 插入测试消息
        cursor.execute(
            "INSERT INTO mm(name, msg, time) VALUES (?, ?, ?)",
            ("testuser", "这是一条测试消息", "2023-01-01 12:00:00")
        )
        conn.commit()
        
        # 验证消息是否插入成功
        cursor.execute("SELECT msg FROM mm WHERE name = ?", ("testuser",))
        result = cursor.fetchone()
        if result and result['msg'] == "这是一条测试消息":
            print("✓ 消息发送成功")
        else:
            print("✗ 消息发送失败")
            conn.close()
            return False
        
        # 清理测试消息
        cursor.execute("DELETE FROM mm WHERE name = ?", ("testuser",))
        conn.commit()
        conn.close()
        print("✓ 测试消息已清理")
    except Exception as e:
        print(f"✗ 消息发送测试失败: {e}")
        return False
    return True

def main():
    """主函数"""
    print("开始测试聊天应用的SQLite3数据库功能...\n")
    
    tests = [
        test_database_connection,
        test_database_tables,
        test_user_registration,
        test_message_sending
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()  # 添加空行分隔
    
    print(f"测试完成: {passed} 个通过, {failed} 个失败")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！SQLite3数据库配置正确。")
        return True
    else:
        print(f"\n❌ {failed} 个测试失败，请检查配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)