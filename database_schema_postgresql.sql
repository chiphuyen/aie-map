-- AIE Map Database Schema for PostgreSQL

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    short_name VARCHAR(10) NOT NULL UNIQUE, -- 'AIE' or 'DMLS'
    pin_color VARCHAR(7) NOT NULL -- hex color codes
);

-- Cities table for locations
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    state VARCHAR(255), -- State/Province/Region (optional)
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    UNIQUE(name, country, state)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
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
CREATE TABLE IF NOT EXISTS review_assets (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(50), -- image, document, etc.
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

-- Admin sessions table for authentication
CREATE TABLE IF NOT EXISTS admin_sessions (
    id VARCHAR(255) PRIMARY KEY,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reviews_book_id ON reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_reviews_city_id ON reviews(city_id);
CREATE INDEX IF NOT EXISTS idx_reviews_company ON reviews(company);
CREATE INDEX IF NOT EXISTS idx_cities_name_country ON cities(name, country);
CREATE INDEX IF NOT EXISTS idx_review_assets_review_id ON review_assets(review_id);

-- Insert default books only if they don't exist
INSERT INTO books (title, short_name, pin_color) 
VALUES 
    ('AI Engineering', 'AIE', '#FF0000'),
    ('Designing Machine Learning Systems', 'DMLS', '#00FF00')
ON CONFLICT (short_name) DO NOTHING;