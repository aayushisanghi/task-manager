CREATE DATABASE tasksdb;
use tasksdb;

CREATE TABLE IF NOT EXISTS tasks (
    `id` varchar(500) PRIMARY KEY,
    `title` varchar(500) NOT NULL,
    `is_completed` INTEGER NOT NULL,
    `notify` varchar(500) NOT NULL
);

INSERT INTO tasks VALUES
    ('task1', 'Test 1', 1, 'aayu.sanghi@gmail.com'),
    ('task2','Test 2', 1, 'aayu.sanghi@gmail.com');
