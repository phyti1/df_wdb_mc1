USE wdb;

CREATE TABLE TMDB_movie_infos (
	movie_id INT PRIMARY KEY AUTO_INCREMENT,
	title VARCHAR(100),
	description TEXT,
	vote_average FLOAT,
	vote_count INT,
	year INT
);

CREATE TABLE user (
	user_id INT PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(50)
);

CREATE TABLE user_rating (
	rating_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT,
    movie_id INT,
	rating float,
	FOREIGN KEY (movie_id) REFERENCES TMDB_movie_infos(movie_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);
