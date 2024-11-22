CREATE DATABASE asudb;
USE asudb;

-- Create Table with region based partitions
CREATE TABLE users (
    id SERIAL NOT NULL,
    region STRING NOT NULL,
    name STRING NOT NULL,
    PRIMARY KEY (region, id)
) PARTITION BY LIST (region) (
    PARTITION tempe VALUES IN ('tempe'),
    PARTITION poly VALUES IN ('poly'),
    PARTITION downtown VALUES IN ('downtown')
);


-- Create user and grant permissions
CREATE USER charu WITH PASSWORD 'charu123';
GRANT ALL ON DATABASE asudb TO charu;

-- Set zone config for partitons

ALTER PARTITION tempe OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 1,
    constraints = '{+region=tempe}',
    lease_preferences = '[[+region=tempe]]';

SELECT pg_sleep(2);
ALTER PARTITION poly OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 1,
    constraints = '{+region=poly}',
    lease_preferences = '[[+region=poly]]';

SELECT pg_sleep(2);
ALTER PARTITION downtown OF TABLE users
CONFIGURE ZONE USING
    num_replicas = 1,
    constraints = '{+region=downtown}',
    lease_preferences = '[[+region=downtown]]';


SELECT pg_sleep(2);
-- Insert sample data
INSERT INTO users (region, name) VALUES
    ('tempe', 'Alice'),
    ('tempe', 'Bob'),
    ('tempe', 'Charlie'),
    ('poly', 'David'),
    ('poly', 'Eve'),
    ('poly', 'Frank'),
    ('downtown', 'Grace'),
    ('downtown', 'Heidi'),
    ('downtown', 'Ivan');
