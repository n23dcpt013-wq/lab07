-- Create schema & seed data for lab07
CREATE DATABASE IF NOT EXISTS atm_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE atm_demo;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
  account_id INT PRIMARY KEY AUTO_INCREMENT,
  holder_name VARCHAR(100) NOT NULL,
  balance DECIMAL(16,2) NOT NULL DEFAULT 0
);

CREATE TABLE cards (
  card_no VARCHAR(32) PRIMARY KEY,
  account_id INT NOT NULL,
  pin_hash CHAR(64) NOT NULL,
  CONSTRAINT fk_cards_acc FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE transactions (
  tx_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  account_id INT NOT NULL,
  card_no VARCHAR(32) NOT NULL,
  atm_id INT NOT NULL,
  tx_type ENUM('WITHDRAW') NOT NULL,
  amount DECIMAL(16,2) NOT NULL,
  balance_after DECIMAL(16,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_acc_time (account_id, created_at)
);

-- Seed
INSERT INTO accounts(holder_name, balance) VALUES ('Nguyen Van A', 5000000.00);
-- Demo card: 6222020000001234, PIN: 123456
INSERT INTO cards(card_no, account_id, pin_hash)
SELECT '6222020000001234', account_id, SHA2('123456', 256) FROM accounts LIMIT 1;
