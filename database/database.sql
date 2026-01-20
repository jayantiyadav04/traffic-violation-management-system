-- Smart Traffic Violation Management System
-- Database Schema

-- Table: Users
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'officer', 'citizen') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Violation Types
CREATE TABLE violation_types (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    base_fine DECIMAL(10, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Areas
CREATE TABLE areas (
    area_id INT PRIMARY KEY AUTO_INCREMENT,
    area_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Violations
CREATE TABLE violations (
    violation_id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_number VARCHAR(20) NOT NULL,
    user_id INT,
    type_id INT NOT NULL,
    area_id INT NOT NULL,
    officer_id INT NOT NULL,
    violation_date DATETIME NOT NULL,
    fine_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('unpaid', 'paid', 'disputed') DEFAULT 'unpaid',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (type_id) REFERENCES violation_types(type_id),
    FOREIGN KEY (area_id) REFERENCES areas(area_id),
    FOREIGN KEY (officer_id) REFERENCES users(user_id)
);

-- Table: Payments
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    violation_id INT NOT NULL,
    payment_date DATETIME NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('cash', 'card', 'online', 'cheque') NOT NULL,
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (violation_id) REFERENCES violations(violation_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_vehicle_number ON violations(vehicle_number);
CREATE INDEX idx_violation_date ON violations(violation_date);
CREATE INDEX idx_status ON violations(status);
CREATE INDEX idx_user_violations ON violations(user_id);

-- Sample Data Insertion

-- Insert sample users
INSERT INTO users (username, password, full_name, role, email, phone) VALUES
('admin', 'admin123', 'Jayanti', 'admin', 'jayant_i@traffic.gov', '1234567890'),
('officer1', 'officer123', 'Rohit Verma', 'officer', 'rohit.verma@traffic.gov', '9876543210'),
('officer2', 'officer123', 'Neha Iyer', 'officer', 'neha.iyer@traffic.gov', '9876543211'),
('citizen1', 'citizen123', 'Rakesh Kumar', 'citizen', 'rakesh.k@email.com', '5551234567'),
('citizen2', 'citizen123', 'Pooja Singh', 'citizen', 'pooja.s@email.com', '5551234568');

-- Insert violation types
INSERT INTO violation_types (type_name, base_fine, description) VALUES
('Speeding', 500.00, 'Exceeding speed limit'),
('Red Light Violation', 1000.00, 'Running a red traffic signal'),
('No Helmet', 300.00, 'Riding without helmet (two-wheeler)'),
('Wrong Parking', 200.00, 'Parking in no-parking zone'),
('DUI', 5000.00, 'Driving under influence'),
('No Seat Belt', 500.00, 'Not wearing seat belt'),
('Mobile Phone Usage', 750.00, 'Using mobile while driving'),
('Wrong Side Driving', 1500.00, 'Driving on wrong side of road'),
('No License', 2000.00, 'Driving without valid license'),
('Overloading', 800.00, 'Vehicle overloaded beyond capacity');

-- Insert areas
INSERT INTO areas (area_name, city) VALUES
('MG Road', 'Bangalore'),
('Connaught Place', 'Delhi'),
('Marine Drive', 'Mumbai'),
('Anna Salai', 'Chennai'),
('Park Street', 'Kolkata'),
('Banjara Hills', 'Hyderabad'),
('Ashram Road', 'Ahmedabad'),
('MI Road', 'Jaipur');

-- Insert sample violations
INSERT INTO violations (vehicle_number, user_id, type_id, area_id, officer_id, violation_date, fine_amount, status) VALUES
('KA01AB1234', 4, 1, 1, 2, '2024-12-15 10:30:00', 500.00, 'paid'),
('DL02CD5678', 5, 2, 2, 2, '2024-12-20 14:45:00', 1000.00, 'unpaid'),
('MH03EF9012', 4, 3, 3, 3, '2025-01-05 09:15:00', 300.00, 'paid'),
('TN04GH3456', 5, 7, 4, 2, '2025-01-08 16:20:00', 750.00, 'unpaid'),
('KA01AB1234', 4, 6, 1, 3, '2025-01-10 11:00:00', 500.00, 'unpaid'),
('WB05IJ7890', 4, 4, 5, 2, '2025-01-12 13:30:00', 200.00, 'paid'),
('TS06KL2345', 5, 8, 6, 3, '2025-01-13 17:45:00', 1500.00, 'unpaid'),
('GJ07MN6789', 4, 1, 7, 2, '2025-01-14 08:00:00', 500.00, 'paid');

-- Insert sample payments
INSERT INTO payments (violation_id, payment_date, amount_paid, payment_method, transaction_id) VALUES
(1, '2024-12-16 10:00:00', 500.00, 'online', 'TXN001234567'),
(3, '2025-01-06 14:30:00', 300.00, 'card', 'TXN001234568'),
(6, '2025-01-13 09:15:00', 200.00, 'cash', 'CASH001'),
(8, '2025-01-15 11:45:00', 500.00, 'online', 'TXN001234569');

-- Useful Queries

-- 1. Get all unpaid violations with details
SELECT 
    v.violation_id,
    v.vehicle_number,
    u.full_name AS owner_name,
    vt.type_name,
    a.area_name,
    v.violation_date,
    v.fine_amount,
    v.status
FROM violations v
LEFT JOIN users u ON v.user_id = u.user_id
JOIN violation_types vt ON v.type_id = vt.type_id
JOIN areas a ON v.area_id = a.area_id
WHERE v.status = 'unpaid'
ORDER BY v.violation_date DESC;

-- 2. Get total fines by payment status
SELECT 
    status,
    COUNT(*) AS total_violations,
    SUM(fine_amount) AS total_amount
FROM violations
GROUP BY status;

-- 3. Get violations by area
SELECT 
    a.area_name,
    a.city,
    COUNT(v.violation_id) AS violation_count,
    SUM(v.fine_amount) AS total_fines
FROM areas a
LEFT JOIN violations v ON a.area_id = v.area_id
GROUP BY a.area_id, a.area_name, a.city
ORDER BY violation_count DESC;

-- 4. Get most common violation types
SELECT 
    vt.type_name,
    COUNT(v.violation_id) AS occurrence_count,
    SUM(v.fine_amount) AS total_fines_collected
FROM violation_types vt
LEFT JOIN violations v ON vt.type_id = v.type_id
GROUP BY vt.type_id, vt.type_name
ORDER BY occurrence_count DESC;

-- 5. Monthly violation trends
SELECT 
    DATE_FORMAT(violation_date, '%Y-%m') AS month,
    COUNT(*) AS total_violations,
    SUM(fine_amount) AS total_fines,
    SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) AS collected_amount
FROM violations
GROUP BY DATE_FORMAT(violation_date, '%Y-%m')
ORDER BY month DESC;

-- 6. Get citizen's violation history
SELECT 
    v.violation_id,
    v.vehicle_number,
    vt.type_name,
    a.area_name,
    v.violation_date,
    v.fine_amount,
    v.status,
    p.payment_date,
    p.payment_method
FROM violations v
JOIN violation_types vt ON v.type_id = vt.type_id
JOIN areas a ON v.area_id = a.area_id
LEFT JOIN payments p ON v.violation_id = p.violation_id
WHERE v.user_id = 4  -- Replace with actual user_id
ORDER BY v.violation_date DESC;

-- 7. Officer performance report
SELECT 
    u.full_name AS officer_name,
    COUNT(v.violation_id) AS violations_registered,
    SUM(v.fine_amount) AS total_fines_imposed,
    SUM(CASE WHEN v.status = 'paid' THEN 1 ELSE 0 END) AS paid_count
FROM users u
LEFT JOIN violations v ON u.user_id = v.officer_id
WHERE u.role = 'officer'
GROUP BY u.user_id, u.full_name
ORDER BY violations_registered DESC;