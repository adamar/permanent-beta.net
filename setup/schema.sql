CREATE DATABASE permanentbeta;

USE permanentbeta;

CREATE TABLE users (
    user_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_login          varchar(64) NOT NULL,
    user_password       varchar(180) NOT NULL,
    user_email          varchar(64),  # Optional, see settings
    user_status         enum('active','disabled')
);

CREATE TABLE items (
    item_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    item_uri		text,
    item_title          varchar(255),
    item_domain         varchar(30),
    item_votes          int,
    item_user_id        int,
    item_status         enum('active','disabled'),
    item_created        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE votes (
    vote_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    item_id             int,
    user_id             int,
    vote_created        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX ix_item_uri ON items (item_uri(255));

CREATE USER 'torndb'@'localhost' IDENTIFIED BY 'xl[daaiqj91d19d';
GRANT INSERT,UPDATE,SELECT on permanentbeta.* to torndb@localhost;

