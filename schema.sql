DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS reviews;

CREATE TABLE songs (
    album TEXT NOT NULL,
    artist TEXT NOT NULL,
    song TEXT NOT NULL,
    album_cover BLOB NOT NULL,
    review TEXT NOT NULL,
    plays INTEGER
);
