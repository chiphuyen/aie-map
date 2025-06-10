-- AIE Map Database Schema

-- Books table
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    short_name VARCHAR(10) NOT NULL UNIQUE, -- 'AIE' or 'DMLS'
    pin_color VARCHAR(7) NOT NULL -- hex color codes
);

-- Cities table for locations
CREATE TABLE cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    UNIQUE(name, country)
);

-- Reviews table
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    city_id INTEGER NOT NULL,
    review_text TEXT,
    reviewer_name VARCHAR(255),
    company VARCHAR(255),
    role VARCHAR(255),
    review_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    original_post_url TEXT,
    social_media_url TEXT,
    screenshot_path VARCHAR(500),
    source VARCHAR(255), -- GoodReads, Amazon, LinkedIn, etc.
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Review assets table for storing multiple pictures/files per review
CREATE TABLE review_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(50), -- image, document, etc.
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

-- Insert default books
INSERT INTO books (title, short_name, pin_color) VALUES 
('AI Engineering', 'AIE', '#FF0000'),
('Designing Machine Learning Systems', 'DMLS', '#00FF00');

-- Example cities (can be populated dynamically)
INSERT INTO cities (name, country, latitude, longitude) VALUES 
('San Francisco', 'United States', 37.7749, -122.4194),
('New York', 'United States', 40.7128, -74.0060),
('London', 'United Kingdom', 51.5074, -0.1278),
('Tokyo', 'Japan', 35.6762, 139.6503);