-- 🚀 DELETE & RECREATE (Run this first)
DROP DATABASE IF EXISTS xship;
CREATE DATABASE xship;
USE xship;

-- TABLES
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'staff', 'client') DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parcels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    sender_name VARCHAR(100),
    sender_address TEXT,
    sender_mobile VARCHAR(15),
    receiver_name VARCHAR(100),
    receiver_address TEXT,
    receiver_mobile VARCHAR(15),
    parcel_type VARCHAR(50),
    parcel_name VARCHAR(100),
    out_date DATE,
    expected_delivery DATE,
    delivered_date DATE,
    status ENUM('pending','picked','in_transit','out_for_delivery','delivered','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parcel_id INT,
    amount DECIMAL(10,2),
    payment_type ENUM('cod', 'online'),
    status ENUM('pending', 'completed', 'failed'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parcel_id) REFERENCES parcels(id)
);

-- 🔥 DIFFERENT PLAIN TEXT PASSWORDS ✅
INSERT INTO users (name, email, password, role) VALUES 
('Super Admin', 'admin@xship.com', 'admin123', 'admin'),
('Delivery Staff', 'staff@xship.com', 'staff456', 'staff'),
('Customer', 'client@xship.com', 'client789', 'client');

-- Demo Parcels
INSERT INTO parcels (tracking_number, sender_name, receiver_name, status) VALUES 
('XSHIP001', 'John Doe', 'Jane Smith', 'delivered'),
('XSHIP002', 'Acme Corp', 'Tech Ltd', 'in_transit'),
('XSHIP003', 'Bob Wilson', 'Alice Brown', 'pending');