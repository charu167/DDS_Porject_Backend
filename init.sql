CREATE DATABASE asudb;
USE asudb;

-- Create Table with region based partitions
CREATE TABLE users (
    id SERIAL NOT NULL,
    region STRING NOT NULL,
    name STRING NOT NULL,
    PRIMARY KEY (region, id)
) PARTITION BY LIST (region) (
    PARTITION US VALUES IN ('US'),
    PARTITION EU VALUES IN ('EU'),
    PARTITION China VALUES IN ('China'),
    PARTITION India VALUES IN ('India')
);


-- Create user and grant permissions
CREATE USER charu WITH PASSWORD 'charu123';
GRANT admin TO charu;
-- GRANT ALL ON DATABASE asudb TO charu;

-- Set zone config for partitons

ALTER PARTITION US OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 4;
    -- constraints = '{+region=tempe}',
    -- lease_preferences = '[[+region=US]]';

SELECT pg_sleep(2);
ALTER PARTITION EU OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 4;
    -- constraints = '{+region=poly}',
    -- lease_preferences = '[[+region=EU]]';

SELECT pg_sleep(2);
ALTER PARTITION China OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 4;
    -- constraints = '{+region=downtown}',
    -- lease_preferences = '[[+region=China]]';

SELECT pg_sleep(2);
ALTER PARTITION India OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 4;
    -- constraints = '{+region=downtown}',
    -- lease_preferences = '[[+region=India]]';


SELECT pg_sleep(2);
-- Insert sample data
INSERT INTO users (region, name) VALUES
    ('US', 'Alice'),
    ('US', 'Bob'),
    ('US', 'Charlie'),
    ('EU', 'David'),
    ('EU', 'Eve'),
    ('EU', 'Frank'),
    ('China', 'Grace'),
    ('China', 'Heidi'),
    ('China', 'Ivan'),
    ('India', 'Raman'),
    ('India', 'Naresh'),
    ('India', 'Kavita');
