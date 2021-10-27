CREATE DATABASE magic;
USE magic;

DROP TABLE IF EXISTS mtgNames;

CREATE TABLE mtgNames 
(
    cardName VARCHAR(30) UNIQUE NOT NULL,
    qty INT UNIQUE NOT NULL,
    price FLOAT,
    PRIMARY KEY (cardName)
)

insert into mtgNames values
("Trained Caracal", 3, 0.30),
("Liliana Vess", 2, 15),
("Thragtusk", 10, 1.00);