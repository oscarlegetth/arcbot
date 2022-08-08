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
    username TEXT PRIMARY KEY,
    val INT
);

CREATE TABLE IF NOT EXISTS coins(
    username TEXT PRIMARY KEY,
    val INT
);

CREATE TABLE IF NOT EXISTS hcim_bets(
    username TEXT PRIMARY KEY,
    bet INT
);

CREATE TABLE IF NOT EXISTS ships(
    username TEXT PRIMARY KEY,
    hull INT,
    cannons INT,
    sails INT,
    cargo_current_amount INT,
    cargo_capacity INT,
    crew_current_amount INT,
    crew_capacity INT
);

CREATE TABLE IF NOT EXISTS commands(
    command_name TEXT PRIMARY KEY,
    command_output TEXT,
    number_of_times_used INT,
    added_by TEXT,
    added_at TEXT
);
