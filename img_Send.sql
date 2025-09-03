
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
 );

 -- 创建索引以提高查询性能
 CREATE INDEX idx_image_sender ON private_image_messages(sender_name);
 CREATE INDEX idx_image_receiver ON private_image_messages(receiver_name);