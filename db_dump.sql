CREATE DATABASE coffer;
CREATE USER coffer WITH ENCRYPTED PASSWORD 'coffer';
GRANT ALL PRIVILEGES ON DATABASE coffer TO coffer;

\c coffer

CREATE TABLE IF NOT EXISTS address_balances (
	address VARCHAR(35) PRIMARY KEY,
	balance BIGINT DEFAULT 0
);
ALTER TABLE address_balances OWNER TO coffer;
