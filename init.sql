CREATE DATABASE asudb;

USE asudb;

-- Create Table with region based partitions
CREATE TABLE
    users (
        id SERIAL NOT NULL,
        region STRING NOT NULL,
        name STRING NOT NULL,
        balance DECIMAL DEFAULT 1000 NOT NULL,
        PRIMARY KEY (region, id)
    )
PARTITION BY
    LIST (region) (
        PARTITION eu
        VALUES
            IN ('eu'),
            PARTITION us
        VALUES
            IN ('us'),
            PARTITION asia
        VALUES
            IN ('asia')
    );

CREATE TABLE
    transactions (
        transaction_id SERIAL NOT NULL,
        sender_id INT NOT NULL,
        sender_region STRING NOT NULL,
        receiver_id INT NOT NULL,
        receiver_region STRING NOT NULL,
        amount DECIMAL NOT NULL,
        transaction_time TIMESTAMP DEFAULT current_timestamp() NOT NULL,
        description STRING,
        PRIMARY KEY (transaction_id),
        FOREIGN KEY (sender_region, sender_id) REFERENCES users (region, id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_region, receiver_id) REFERENCES users (region, id) ON DELETE CASCADE
    );

-- Create user and grant permissions
CREATE USER charu
WITH
    PASSWORD 'charu123';

-- GRANT ALL ON DATABASE asudb TO charu;
GRANT admin TO charu;

SELECT
    pg_sleep (2);

-- Set zone config for partitons
ALTER PARTITION eu OF TABLE users CONFIGURE ZONE USING num_replicas = 3,
constraints = '[+region=eu]',
lease_preferences = '[[+region=eu]]';

SELECT
    pg_sleep (2);

ALTER PARTITION us OF TABLE users CONFIGURE ZONE USING num_replicas = 3,
constraints = '[+region=us]',
lease_preferences = '[[+region=us]]';

SELECT
    pg_sleep (2);

ALTER PARTITION asia OF TABLE users CONFIGURE ZONE USING num_replicas = 3,
constraints = '[+region=asia]',
lease_preferences = '[[+region=asia]]';

SELECT
    pg_sleep (2);

-- Insert sample data
INSERT INTO
    users (region, name)
VALUES
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
    ('asia', 'Zara');