FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'p';

DROP DATABASE IF EXISTS MotionPictureDB;
CREATE DATABASE MotionPictureDB;

USE MotionPictureDB;

CREATE TABLE MotionPicture (
id int NOT NULL PRIMARY KEY,
name varchar(255),
rating int CHECK (rating >= 0 AND rating <= 10),
production varchar(255),
budget BIGINT CHECK (budget > 0)
);

CREATE TABLE People (
id int NOT NULL PRIMARY KEY,
name varchar(255),
nationality varchar(255),
dob varchar(255),
gender varchar(1)
);

CREATE TABLE User (
email varchar(255) NOT NULL PRIMARY KEY,
name varchar(255),
age int CHECK (age > 18));

CREATE TABLE Likes (
uemail VARCHAR(255) NOT NULL,
mpid int NOT NULL,
PRIMARY KEY (uemail, mpid),
CONSTRAINT fk_user_likes
	FOREIGN KEY (uemail) REFERENCES User(email) ON DELETE CASCADE,
CONSTRAINT fk_mpid_likes
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE);

CREATE TABLE Movie (
mpid int NOT NULL PRIMARY KEY,
boxoffice_collection float CHECK (boxoffice_collection >= 0),
CONSTRAINT fk_mp_movie
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE);
	
CREATE TABLE Series (
mpid int NOT NULL PRIMARY KEY,
season_count float CHECK (season_count >= 1),
CONSTRAINT fk_mp_series
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE);
	
CREATE TABLE Role (
mpid int NOT NULL,
pid int NOT NULL,
role_name VARCHAR(255),
PRIMARY KEY (mpid, pid, role_name),
CONSTRAINT fk_mp_role
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
CONSTRAINT fk_people_role
	FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE);
	
CREATE TABLE Award (
mpid int NOT NULL,
pid int NOT NULL,
award_name VARCHAR(255),
award_year int,
PRIMARY KEY (mpid, pid, award_name, award_year),
CONSTRAINT fk_mp_award
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
CONSTRAINT fk_people_award
	FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE);

CREATE TABLE Genre (
mpid int NOT NULL,
genre_name VARCHAR(255),
PRIMARY KEY (mpid, genre_name),
CONSTRAINT fk_mp_genre
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE);
	
CREATE TABLE Location (
mpid int NOT NULL,
zip int,
city VARCHAR(255),
country VARCHAR(255),
PRIMARY KEY (mpid, zip),
CONSTRAINT fk_mp_location
	FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE);
