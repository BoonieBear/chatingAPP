-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    s_name VARCHAR(255) NOT NULL UNIQUE,
    s_phone_num VARCHAR(20),
    s_sex VARCHAR(10),
    place VARCHAR(255),
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建漂流瓶消息表
CREATE TABLE IF NOT EXISTS mm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    msg TEXT NOT NULL,
    time DATETIME NOT NULL,
    is_persistent TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建私聊文本消息表
CREATE TABLE IF NOT EXISTS private_text_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_name VARCHAR(255) NOT NULL,
    receiver_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    send_time DATETIME NOT NULL,
    is_read TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建私聊图片消息表
CREATE TABLE IF NOT EXISTS private_image_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_name VARCHAR(75) NOT NULL,
    receiver_name VARCHAR(75) NOT NULL,
    image_data LONGBLOB,  -- 使用LONGBLOB存储图片二进制数据
    image_type VARCHAR(20),  -- 存储图片类型（如jpg, png等）
    image_size INT,  -- 存储图片大小
    send_time VARCHAR(22) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sender_name) REFERENCES users(s_name),
    FOREIGN KEY (receiver_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建索引以提高查询性能
CREATE INDEX idx_image_sender ON private_image_messages(sender_name);
CREATE INDEX idx_image_receiver ON private_image_messages(receiver_name);

-- 创建朋友圈表
CREATE TABLE IF NOT EXISTS moments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    content TEXT,
    image_paths TEXT,
    post_time DATETIME NOT NULL,
    FOREIGN KEY (user_name) REFERENCES users(s_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建朋友圈评论表
CREATE TABLE IF NOT EXISTS moment_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    moment_id INT NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    comment TEXT NOT NULL,
    comment_time DATETIME NOT NULL,
    FOREIGN KEY (moment_id) REFERENCES moments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建朋友圈点赞表
CREATE TABLE IF NOT EXISTS moment_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    moment_id INT NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    like_time DATETIME NOT NULL,
    FOREIGN KEY (moment_id) REFERENCES moments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;