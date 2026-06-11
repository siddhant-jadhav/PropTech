-- ============================================
-- Property Management System - Database Schema
-- ============================================

USE property_management;

-- ============================================
-- Table: users
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager', 'staff') NOT NULL DEFAULT 'staff',
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: properties
-- ============================================
CREATE TABLE IF NOT EXISTS properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    occupancy_status ENUM('occupied', 'vacant') NOT NULL DEFAULT 'vacant',
    monthly_revenue DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_properties_city (city),
    INDEX idx_properties_status (occupancy_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: maintenance_requests
-- ============================================
CREATE TABLE IF NOT EXISTS maintenance_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('pending', 'approved', 'assigned', 'in_progress', 'completed', 'closed', 'rejected') NOT NULL DEFAULT 'pending',
    assigned_to INT DEFAULT NULL,
    approved_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_maintenance_status (status),
    INDEX idx_maintenance_property (property_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: audit_logs
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    action VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Seed Data: Users (placeholder hashes, fixed on startup)
-- ============================================
INSERT INTO users (name, email, password_hash, role, status) VALUES
('Admin User', 'admin@proptech.com', 'placeholder', 'admin', 'active'),
('Sarah Manager', 'sarah@proptech.com', 'placeholder', 'manager', 'active'),
('John Staff', 'john@proptech.com', 'placeholder', 'staff', 'active'),
('Emily Staff', 'emily@proptech.com', 'placeholder', 'staff', 'active'),
('Mike Manager', 'mike@proptech.com', 'placeholder', 'manager', 'active');

-- ============================================
-- Seed Data: Properties
-- ============================================
INSERT INTO properties (property_name, city, address, occupancy_status, monthly_revenue) VALUES
('Skyline Tower A', 'Mumbai', '123 Marine Drive, South Mumbai, Maharashtra 400020', 'occupied', 185000.00),
('Green Valley Apartments', 'Bangalore', '45 MG Road, Indiranagar, Karnataka 560038', 'occupied', 120000.00),
('Sunset Plaza', 'Delhi', '78 Connaught Place, New Delhi 110001', 'vacant', 0.00),
('Lakewood Residences', 'Hyderabad', '90 HITEC City, Madhapur, Telangana 500081', 'occupied', 95000.00),
('Palm Grove Villas', 'Chennai', '12 ECR Road, Sholinganallur, Tamil Nadu 600119', 'occupied', 145000.00),
('Royal Heights', 'Pune', '56 Koregaon Park, Pune, Maharashtra 411001', 'vacant', 0.00),
('Marina Bay Complex', 'Mumbai', '34 Worli Sea Face, Mumbai, Maharashtra 400018', 'occupied', 220000.00),
('Tech Park Suites', 'Bangalore', '88 Whitefield Main Road, Karnataka 560066', 'occupied', 175000.00),
('Heritage Manor', 'Jaipur', '23 Civil Lines, Jaipur, Rajasthan 302006', 'vacant', 0.00),
('Emerald Gardens', 'Kolkata', '67 Park Street, Kolkata, West Bengal 700016', 'occupied', 88000.00),
('Azure Towers', 'Gurgaon', '15 Cyber Hub, DLF Phase 2, Haryana 122002', 'occupied', 198000.00),
('Pearl Residency', 'Ahmedabad', '40 SG Highway, Bodakdev, Gujarat 380054', 'vacant', 0.00);

-- ============================================
-- Seed Data: Maintenance Requests
-- ============================================
INSERT INTO maintenance_requests (property_id, title, description, status, assigned_to, approved_by) VALUES
(1, 'Elevator Repair', 'Main elevator in Tower A is malfunctioning. Needs urgent repair.', 'completed', 3, 2),
(2, 'Plumbing Issue - Unit 302', 'Water leakage in bathroom of unit 302. Tenant reported flooding.', 'in_progress', 4, 2),
(3, 'Paint Touch-up', 'Lobby walls need repainting before new tenant moves in.', 'approved', NULL, 5),
(4, 'HVAC Maintenance', 'Annual AC servicing for all units in the building.', 'assigned', 4, 2),
(5, 'Security Camera Installation', 'Install 4 new CCTV cameras in parking area.', 'pending', NULL, NULL),
(7, 'Fire Alarm Testing', 'Quarterly fire alarm system testing and certification.', 'closed', 3, 2),
(8, 'Parking Lot Resurfacing', 'Parking area has developed cracks and potholes.', 'pending', NULL, NULL),
(1, 'Gym Equipment Repair', 'Treadmill and elliptical machine need servicing.', 'assigned', 4, 2),
(10, 'Window Replacement', 'Broken windows in unit 501 need immediate replacement.', 'approved', NULL, 5),
(11, 'Landscaping', 'Garden area maintenance and new plant installation.', 'in_progress', 4, 2);

-- ============================================
-- Seed Data: Audit Logs
-- ============================================
INSERT INTO audit_logs (user_id, action) VALUES
(1, 'SYSTEM_INIT: Database initialized with seed data'),
(1, 'CREATE_PROPERTY: Added Skyline Tower A'),
(1, 'CREATE_PROPERTY: Added Green Valley Apartments'),
(2, 'CREATE_MAINTENANCE: Elevator Repair for Skyline Tower A'),
(2, 'UPDATE_MAINTENANCE: Marked Elevator Repair as completed'),
(1, 'CREATE_USER: Added staff member John Staff'),
(5, 'CREATE_MAINTENANCE: Plumbing Issue for Green Valley Apartments');
