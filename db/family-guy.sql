CREATE DATABASE magic;
USE magic;

DROP TABLE IF EXISTS familyguyfunny;

CREATE TABLE familyguyfunny 
(
    Firstname VARCHAR(30) NOT NULL PRIMARY KEY,
    Lastname VARCHAR(30) NOT NULL UNIQUE,
    Age INT NOT NULL,
    Hometown VARCHAR(30),
    Job VARCHAR(30)
);

insert into familyguyfunny values
("Peter", "Griffin", 41, "Quahog", "Brewery"),
("Jaret", "Varn", 69, "London", "Cutie"),
("Ligma", "Sugma", 1000, "England", "Stank")