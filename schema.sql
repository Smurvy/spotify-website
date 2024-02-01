DROP TABLE IF EXISTS songs;

CREATE TABLE posts (
    song TEXT NOT NULL,
    album TEXT NOT NULL,
    artist TEXT NOT NULL,
    content TEXT NOT NULL
);