CREATE DATABASE asudb;
USE asudb;

-- Create Table with region based partitions
CREATE TABLE users (
    id SERIAL NOT NULL,
    region STRING NOT NULL,
    name STRING NOT NULL,
    PRIMARY KEY (region, id)
) PARTITION BY LIST (region) (
    PARTITION eu VALUES IN ('eu'),
    PARTITION us VALUES IN ('us'),
    PARTITION asia VALUES IN ('asia'),
    PARTITION africa VALUES IN ('africa')
);


-- Create user and grant permissions
CREATE USER charu WITH PASSWORD 'charu123';
GRANT admin TO charu;
-- GRANT ALL ON DATABASE asudb TO charu;

-- Set zone config for partitons
-- eu data resides in eu, us, asia, africa
SELECT pg_sleep(2);
ALTER PARTITION eu OF TABLE users
CONFIGURE ZONE USING
    -- num_replicas = 2,
    constraints = '[+region=eu]',
    lease_preferences = '[[+region=eu]]';

-- us data resides in eu, us, asia, africa
SELECT pg_sleep(2);
ALTER PARTITION us OF TABLE users
CONFIGURE ZONE USING
    -- num_replicas = 2,
    constraints = '[+region=us]',
    lease_preferences = '[[+region=us]]';

-- asia data resides in eu, us, asia, africa
SELECT pg_sleep(2);
ALTER PARTITION asia OF TABLE users
CONFIGURE ZONE USING
    -- num_replicas = 2,
    constraints = '[+region=asia]',
    lease_preferences = '[[+region=asia]]';

-- africa data resides in eu, us, asia, africa
SELECT pg_sleep(2);
ALTER PARTITION africa OF TABLE users
CONFIGURE ZONE USING
    -- num_replicas = 2,
    constraints = '[+region=africa]',
    lease_preferences = '[[+region=africa]]';


SELECT pg_sleep(2);
-- Insert sample data
INSERT INTO users (region, name) VALUES
    -- US Region
    ('us', 'Alice'),
    ('us', 'Bob'),
    ('us', 'Charlie'),
    ('us', 'Diana'),
    ('us', 'Edward'),
    ('us', 'Fiona'),
    ('us', 'George'),
    ('us', 'Hannah'),
    ('us', 'Ian'),
    ('us', 'Jane'),

    -- EU Region
    ('eu', 'David'),
    ('eu', 'Eve'),
    ('eu', 'Frank'),
    ('eu', 'Laura'),
    ('eu', 'Michael'),
    ('eu', 'Nina'),
    ('eu', 'Oliver'),
    ('eu', 'Paul'),
    ('eu', 'Quinn'),
    ('eu', 'Rachel'),

    -- Asia Region
    ('asia', 'Grace'),
    ('asia', 'Heidi'),
    ('asia', 'Ivan'),
    ('asia', 'Sunil'),
    ('asia', 'Priya'),
    ('asia', 'Ravi'),
    ('asia', 'Sneha'),
    ('asia', 'Tina'),
    ('asia', 'Vikram'),
    ('asia', 'Zara'),

    -- Africa Region
    ('africa', 'Raman'),
    ('africa', 'Naresh'),
    ('africa', 'Kavita'),
    ('africa', 'Abdul'),
    ('africa', 'Bola'),
    ('africa', 'Chidi'),
    ('africa', 'Dalia'),
    ('africa', 'Ekon'),
    ('africa', 'Fatima'),
    ('africa', 'Gabriel');

