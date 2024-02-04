DROP TABLE IF EXISTS songs;

CREATE TABLE reviews (
    song TEXT NOT NULL,
    rating INTEGER,
    review TEXT NOT NULL
);