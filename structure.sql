USE cds;

CREATE TABLE TMDB_movie_infos (
	movie_id INT PRIMARY KEY,
	title VARCHAR(100),
	description TEXT,
	vote_average FLOAT,
	vote_count INT,
	year INT
);

CREATE TABLE user (
	user_id VARCHAR(50) PRIMARY KEY,
	name VARCHAR(50)
);

CREATE TABLE user_rating (
	rating_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id VARCHAR(50),
	rating float,
    movie_id INT,
	FOREIGN KEY (movie_id) REFERENCES TMDB_movie_infos(movie_id),
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);
