CREATE DATABASE magic;
USE magic;

DROP TABLE IF EXISTS mtgCards;

CREATE TABLE mtgCards
(
    cardName VARCHAR(30) UNIQUE NOT NULL,
    qty INT NOT NULL,
    price FLOAT,
    PRIMARY KEY (cardName)
);

insert into mtgCards values
("Trained Caracal", 3, 0.30),
("Liliana Vess", 2, 15),
("Thragtusk", 10, 1.00),
("Fury Sliver", 10, 1.00),
("Prowling Serpopard", 10, 2.00),
("Jace, the Mind Sculptor", 15, 150.00),
("Flickerwisp", 10, 10.00),
("Squadron Hawk", 10, 1.00),
("Abrupt Decay", 5, 31.00),
("Kitchen Finks", 2, 10.00),
("Siege Rhino", 5, 2.00);