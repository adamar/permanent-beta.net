CREATE DATABASE permanentbeta;

USE permanentbeta;

CREATE TABLE users (
    user_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_login          varchar(64) NOT NULL,
    user_password       varchar(180) NOT NULL,
    user_email          varchar(64),  # Optional, see settings
    user_status         enum('active','disabled')
);

CREATE UNIQUE INDEX ix_users_login ON users (user_login(64));

CREATE TABLE items (
    item_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    item_uri		text,
    item_title          varchar(255),
    item_domain         varchar(30),
    item_votes          int default 0,
    item_user_id        int,
    item_status         enum('active','disabled') default 'active',
    item_created        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX ix_item_uri ON items (item_uri(255));

CREATE TABLE votes (
    vote_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    item_user_id        float,
    item_id             int,
    user_id             int,
    vote_created        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_votes_item ON votes (item_id);
CREATE INDEX ix_votes_user ON votes (user_id);
CREATE UNIQUE INDEX ix_votes_item_user ON votes (item_user_id);

CREATE USER 'torndb'@'localhost' IDENTIFIED BY 'xl[daaiqj91d19d';
GRANT INSERT,UPDATE,SELECT on permanentbeta.* to torndb@localhost;

