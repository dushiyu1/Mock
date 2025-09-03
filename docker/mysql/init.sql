CREATE DATABASE IF NOT EXISTS mock_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'mockuser'@'%' IDENTIFIED BY 'mockpassword';
GRANT ALL PRIVILEGES ON mock_server.* TO 'mockuser'@'%';
FLUSH PRIVILEGES;