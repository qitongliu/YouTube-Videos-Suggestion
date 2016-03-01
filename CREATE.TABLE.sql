CREATE TABLE Channel (
c_id VARCHAR(50),
c_title VARCHAR(100),
c_description VARCHAR(5000),
c_view_count INTEGER  CHECK (c_view_count >= 0),
c_sub_count INTEGER CHECK (c_sub_count >= 0),
PRIMARY KEY (c_id));

CREATE TABLE Video (
video_id VARCHAR(50),
channel_id VARCHAR(50),
title VARCHAR(100),
description VARCHAR(5000),
date DATE,
length VARCHAR(20),
embed_code VARCHAR(200),
view_count INTEGER CHECK (view_count >= 0),
like_count INTEGER CHECK (like_count >= 0),
dislike_count INTEGER CHECK (dislike_count >= 0),
PRIMARY KEY (video_id));

CREATE TABLE Users (
user_id INT CHECK (user_id >= 0),
username VARCHAR(50) NOT NULL,
PRIMARY KEY (user_id),
UNIQUE (username));

CREATE TABLE Comment (
com_id VARCHAR(50),
video_id VARCHAR(50) NOT NULL,
text VARCHAR(5000),
com_date DATE,
display_name VARCHAR(300),
profile_img VARCHAR(200),
like_count INTEGER CHECK (like_count >= 0),
PRIMARY KEY (com_id),
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE);

CREATE TABLE Thumbnail (
t_url VARCHAR(200),
t_width INTEGER CHECK (t_width > 0),
t_height INTEGER CHECK (t_height > 0),
PRIMARY KEY (t_url));

CREATE TABLE likes_1 (
user_id INTEGER ,
video_id VARCHAR(50),
PRIMARY KEY (user_id, video_id),
FOREIGN KEY (user_id) REFERENCES Users
ON DELETE CASCADE,
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE);

CREATE TABLE skips (
user_id INTEGER ,
video_id VARCHAR(50),
PRIMARY KEY (user_id, video_id),
FOREIGN KEY (user_id) REFERENCES Users
ON DELETE CASCADE,
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE);

CREATE TABLE watched (
user_id INTEGER ,
video_id VARCHAR(50),
watch_time DATE,
PRIMARY KEY (user_id, video_id, watch_time),
FOREIGN KEY (user_id) REFERENCES Users
ON DELETE CASCADE,
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE);

CREATE TABLE subscribes_to (
user_id INTEGER ,
c_id VARCHAR(50),
PRIMARY KEY (user_id, c_id),
FOREIGN KEY (user_id) REFERENCES Users
ON DELETE CASCADE,
FOREIGN KEY (c_id) REFERENCES Channel
ON DELETE CASCADE);

CREATE TABLE has_thumb_1 (
t_url VARCHAR(200),
video_id VARCHAR(50) NOT NULL,
PRIMARY KEY (t_url, video_id), 
FOREIGN KEY (t_url) REFERENCES Thumbnail
ON DELETE NO ACTION,
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE);

CREATE TABLE has_thumb_2 (
t_url VARCHAR(200),
c_id VARCHAR(50) NOT NULL,
PRIMARY KEY (t_url, c_id),
FOREIGN KEY (t_url) REFERENCES Thumbnail
ON DELETE NO ACTION,
FOREIGN KEY (c_id) REFERENCES Channel
ON DELETE CASCADE);

CREATE TABLE prof_pic (
t_url VARCHAR(200),
user_id INTEGER ,
PRIMARY KEY (t_url, user_id),
FOREIGN KEY (t_url) REFERENCES Thumbnail
ON DELETE SET DEFAULT, 
FOREIGN KEY (user_id) REFERENCES USERS
ON DELETE CASCADE);

CREATE TABLE uploaded_by (
video_id VARCHAR(50),
c_id VARCHAR(50),
PRIMARY KEY (video_id, c_id),
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE,
FOREIGN KEY (c_id) REFERENCES Channel
ON DELETE CASCADE);

CREATE TABLE likes_2 (
video_id VARCHAR(50),
c_id VARCHAR(50),
PRIMARY KEY (video_id, c_id),
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE,
FOREIGN KEY (c_id) REFERENCES Channel
ON DELETE CASCADE);

CREATE TABLE favorites (
video_id VARCHAR(50),
c_id VARCHAR(50),
PRIMARY KEY (video_id, c_id),
FOREIGN KEY (video_id) REFERENCES Video
ON DELETE CASCADE,
FOREIGN KEY (c_id) REFERENCES Channel
ON DELETE CASCADE);
