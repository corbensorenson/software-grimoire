CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  email TEXT NOT NULL,
  birthdate_text VARCHAR,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
