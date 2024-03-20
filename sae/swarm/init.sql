CREATE USER 'toto'@'%' IDENTIFIED BY 'toto';

CREATE DATABASE sae;

GRANT ALL PRIVILEGES ON sae.* TO 'toto'@'%';

FLUSH PRIVILEGES;

USE sae;

CREATE TABLE account (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(40),
    balance INT DEFAULT 0
);
