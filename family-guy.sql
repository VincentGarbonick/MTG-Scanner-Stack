CREATE DATABASE magic;
USE magic;

DROP TABLE IF EXISTS familyguyfunny;

CREATE TABLE familyguyfunny 
(
    FirstName VARCHAR(30) NOT NULL PRIMARY KEY,
    LastName VARCHAR(30) NOT NULL UNIQUE,
    Age INT NOT NULL,
    Hometown VARCHAR(30),
    Job VARCHAR(30),
    id INT 
);

insert into familyguyfunny values
("Peter", "Griffin", 41, "Quahog", "Brewery",1),
("Jaret", "Varn", 69, "London", "Cutie",2),
("Ligma", "Sugma", 1000, "England", "Stank",3)