/*
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS spin_records;
DROP TABLE IF EXISTS timeouts;
*/

CREATE TABLE records(
    username TEXT,
    record_name TEXT,
    val TEXT
);

CREATE TABLE spin_records(
    username TEXT,
    record_name TEXT,
    val TEXT
);

CREATE TABLE timeouts(
    username TEXT,
    val TEXT
);