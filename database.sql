-- Creates the Users table
CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL
);

-- Creates the Crops table
CREATE TABLE crops (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    sowing_date DATE NOT NULL,
    growth_duration_days INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Creates the Logs table
CREATE TABLE logs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    crop_id INTEGER NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    quantity_workers VARCHAR(100) NOT NULL,
    cost FLOAT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY(crop_id) REFERENCES crops(id)
);
