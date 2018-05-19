INSERT INTO users (user_id, user_name)
VALUES
  (1, 'test1'),
  (2, 'test2');

INSERT INTO images (author_id, description, url, likes)
VALUES
  (1, 'test image 1', 'https://i.redd.it/qh713wbo4r8y.jpg',1),
  (2, 'test image 2', 'https://i.redd.it/qh713wbo4r8y.jpg',1);
  
INSERT INTO likes (author_id, image_id)
VALUES
    (2,1),
    (1,2)