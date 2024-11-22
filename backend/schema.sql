-- Create Database
CREATE DATABASE payments;
USE payments;

-- Create accounts table
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    balance DECIMAL(10,2),
    region STRING NOT NULL
);

-- Create payment_transactions table
CREATE TABLE payment_transactions (
    transaction_id UUID DEFAULT gen_random_uuid(),
    amount DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT now(),
    sender_id INT,
    receiver_id INT,
    region STRING NOT NULL,
    PRIMARY KEY (transaction_id, region)
);
