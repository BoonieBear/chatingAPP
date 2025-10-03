-- 添加用户在线状态表
CREATE TABLE IF NOT EXISTS user_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(255) NOT NULL UNIQUE,
    is_online BOOLEAN DEFAULT 0,
    last_seen DATETIME,
    FOREIGN KEY (user_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 添加用户通知表
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'message', 'friend_request', 'system', etc.
    title VARCHAR(255),
    content TEXT,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 添加用户个人资料扩展表
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(255) NOT NULL UNIQUE,
    avatar_path VARCHAR(255),
    bio TEXT,
    birth_date DATE,
    theme_preference VARCHAR(20) DEFAULT 'light',  -- 'light', 'dark', 'auto'
    notification_enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 添加文件分享表
CREATE TABLE IF NOT EXISTS shared_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_name VARCHAR(255) NOT NULL,
    receiver_name VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    send_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_name) REFERENCES users(s_name),
    FOREIGN KEY (receiver_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 为消息表添加撤回相关字段
ALTER TABLE private_text_messages ADD COLUMN is_withdrawn BOOLEAN DEFAULT 0;
ALTER TABLE private_text_messages ADD COLUMN withdrawn_time DATETIME;

ALTER TABLE private_image_messages ADD COLUMN is_withdrawn BOOLEAN DEFAULT 0;
ALTER TABLE private_image_messages ADD COLUMN withdrawn_time DATETIME;

-- 添加撤回通知表
CREATE TABLE IF NOT EXISTS message_withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    message_type VARCHAR(20) NOT NULL,  -- 'text' or 'image'
    sender_name VARCHAR(255) NOT NULL,
    withdrawn_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;