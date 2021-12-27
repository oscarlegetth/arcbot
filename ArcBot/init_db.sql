/*
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS spin_records;
DROP TABLE IF EXISTS timeouts;
*/

CREATE TABLE IF NOT EXISTS records(
    username TEXT,
    record_name TEXT,
    val TEXT
);

CREATE TABLE IF NOT EXISTS spin_records(
    username TEXT,
    record_name TEXT,
    val TEXT
);

CREATE TABLE IF NOT EXISTS timeouts(
    username TEXT,
    val TEXT
);