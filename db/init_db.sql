CREATE TABLE emails (
	id SERIAL PRIMARY KEY,
	email VARCHAR(100)
);

INSERT INTO emails (email) VALUES ('bot@telegram.org'), ('s.dolbikov@yandex.ru');

CREATE TABLE phonenumbers (
	id SERIAL PRIMARY KEY,
	phonenumber VARCHAR(100)
);

INSERT INTO phonenumbers (phonenumber) VALUES ('79001112233'), ('+79123456789');

SELECT pg_create_physical_replication_slot('replication_slot');

