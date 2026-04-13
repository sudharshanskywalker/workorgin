DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS workers;
DROP TABLE IF EXISTS worker_skills;
DROP TABLE IF EXISTS worker_requests;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    icon_name TEXT,
    category TEXT
);

CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    avatar TEXT,
    profession TEXT,
    rating REAL,
    review_count INTEGER,
    location TEXT,
    location TEXT,
    bio TEXT
);

CREATE TABLE worker_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    skill TEXT NOT NULL,
    FOREIGN KEY (worker_id) REFERENCES workers (id)
);

CREATE TABLE worker_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    profession TEXT,
    experience INTEGER,
    location TEXT,
    avatar TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
