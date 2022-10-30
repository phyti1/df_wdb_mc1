USE test;

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

INSERT INTO TMDB_movie_infos (title, description, vote_average, vote_count, year) VALUES ('The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008);
INSERT INTO TMDB_movie_infos (title, description, vote_average, vote_count, year) VALUES ('The Matrix', 'Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.', 82, 2179, 1999);
INSERT INTO TMDB_movie_infos (title, description, vote_average, vote_count, year) VALUES ('Pulp Fiction', 'A burger-loving hit man, his philosophical partner, a drug-addled gangsters moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.', 84, 6213, 1994);
INSERT INTO TMDB_movie_infos (title, description, vote_average, vote_count, year) VALUES ('The Godfather', 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care.', 87, 2184, 1972);
INSERT INTO TMDB_movie_infos (title, description, vote_average, vote_count, year) VALUES ('Scarface', 'After getting a green card in exchange for assassinating a Cuban government official, Tony Montana stakes a claim on the drug trade in Miami. Viciously murdering anyone who stands in his way, Tony eventually becomes the biggest drug lord in the state.', 81, 987, 1983);


INSERT INTO user (name) VALUES ('Hanspeter Peterhans');
INSERT INTO user (name) VALUES ('Werner Würschtli');
INSERT INTO user (name) VALUES ('Chantal Schläppi');

INSERT INTO user_rating (user_id, rating, movie_id) VALUES (1, 93, 1);
INSERT INTO user_rating (user_id, rating, movie_id) VALUES (1, 67, 4);
INSERT INTO user_rating (user_id, rating, movie_id) VALUES (2, 81, 3);
INSERT INTO user_rating (user_id, rating, movie_id) VALUES (2, 51, 1);
INSERT INTO user_rating (user_id, rating, movie_id) VALUES (3, 99, 2);
INSERT INTO user_rating (user_id, rating, movie_id) VALUES (3, 91, 1);
