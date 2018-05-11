DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS likes;

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL
);


CREATE TABLE images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    url TEXT NOT NULL,
    likes INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users (user_id)
);

CREATE TABLE likes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users (user_id),
    FOREIGN KEY (image_id) REFERENCES images (id)
);

INSERT INTO users (user_id, user_name) VALUES (00000,"testuser");
INSERT INTO images (author_id, description, url,likes) VALUES (00000,"test post",
"http://s3.amazonaws.com/cdn-origin-etr.akc.org/wp-content/uploads/2017/11/12225358/Pug-On-White-01.jpg",0);