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
("Thragtusk", 10, 1.00),
("Dummy1", 1, 1),
("Dummy2", 1, 1),
("Dummy3", 1, 1),
("Dummy4", 1, 1),
("Dummy5", 1, 1),
("Dummy6", 1, 1),
("Dummy7", 1, 1),
("Dummy8", 1, 1),
("Dummy9", 1, 1),
("Dummy10", 1, 1),
("Dummy11", 1, 1),
("Dummy12", 1, 1),
("Dummy13", 1, 1),
("Dummy14", 1, 1),
("Dummy15", 1, 1),
("Dummy16", 1, 1),
("Dummy17", 1, 1),
("Dummy18", 1, 1),
("Dummy19", 1, 1),
("Dummy20", 1, 1),
("Dummy21", 1, 1),
("Dummy22", 1, 1),
("Dummy23", 1, 1),
("Dummy24", 1, 1),
("Dummy25", 1, 1),
("Dummy26", 1, 1),
("Dummy27", 1, 1),
("Dummy28", 1, 1),
("Dummy29", 1, 1),
("Dummy30", 1, 1),
("Dummy31", 1, 1),
("Dummy32", 1, 1),
("Dummy33", 1, 1),
("Dummy34", 1, 1);

