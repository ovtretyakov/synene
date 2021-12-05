
-- DROP ROLE synene_handler;

CREATE USER synene WITH PASSWORD 'dummy' CREATEDB;
CREATE USER synene_handler WITH PASSWORD 'dummy' CREATEDB;


CREATE DATABASE dev_synene
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;
GRANT CONNECT, TEMPORARY ON DATABASE dev_synene TO public;
GRANT ALL ON DATABASE dev_synene TO postgres;
GRANT ALL ON DATABASE dev_synene TO synene;
GRANT ALL ON DATABASE dev_synene TO synene_handler;

CREATE DATABASE test_synene
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'Russian_Russia.1251'
       LC_CTYPE = 'Russian_Russia.1251'
       CONNECTION LIMIT = -1;
GRANT CONNECT, TEMPORARY ON DATABASE test_synene TO public;
GRANT ALL ON DATABASE test_synene TO postgres;
GRANT ALL ON DATABASE test_synene TO synene;
GRANT ALL ON DATABASE test_synene TO synene_handler;


-- NEW DATABASE
CREATE SCHEMA synene AUTHORIZATION synene;

GRANT ALL ON SCHEMA synene TO postgres;
GRANT ALL ON SCHEMA synene TO synene_handler;


