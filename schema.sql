DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
    album TEXT NOT NULL,
    artist TEXT NOT NULL,
    song TEXT NOT NULL,
    album_cover BLOB NOT NULL,
    review TEXT NOT NULL
);