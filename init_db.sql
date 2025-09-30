-- 创建数据库
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    s_name VARCHAR(50) NOT NULL UNIQUE,
    s_phone_num VARCHAR(20),
    s_sex VARCHAR(10),
    place VARCHAR(50),
    password VARCHAR(100) NOT NULL
);

-- 创建漂流瓶消息表
CREATE TABLE IF NOT EXISTS mm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    msg TEXT NOT NULL,
    time DATETIME NOT NULL,
    is_persistent TINYINT(1) DEFAULT 0,
    INDEX idx_mm_name (name), -- 添加索引
    INDEX idx_mm_time (time)  -- 添加索引
);

-- 创建私聊消息表
CREATE TABLE IF NOT EXISTS private_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_name VARCHAR(50) NOT NULL,
    receiver_name VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    send_time DATETIME NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    CONSTRAINT fk_private_sender FOREIGN KEY (sender_name) REFERENCES users(s_name) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_private_receiver FOREIGN KEY (receiver_name) REFERENCES users(s_name) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_private_sender (sender_name),
    INDEX idx_private_receiver (receiver_name),
    INDEX idx_private_send_time (send_time)
);

-- 创建私聊图片消息表
CREATE TABLE IF NOT EXISTS private_image_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_name VARCHAR(50) NOT NULL,
    receiver_name VARCHAR(50) NOT NULL,
    image_data LONGBLOB NOT NULL,
    image_type VARCHAR(10) NOT NULL,
    image_size INT NOT NULL,
    send_time DATETIME NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    CONSTRAINT fk_private_image_sender FOREIGN KEY (sender_name) REFERENCES users(s_name) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_private_image_receiver FOREIGN KEY (receiver_name) REFERENCES users(s_name) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_private_image_sender (sender_name),
    INDEX idx_private_image_receiver (receiver_name),
    INDEX idx_private_image_send_time (send_time)
);

