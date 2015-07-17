--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.5
-- Dumped by pg_dump version 9.3.5
-- Started on 2014-11-18 16:49:28 CET

SET statement_timeout = 0;
--SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;


CREATE SCHEMA wns;

ALTER SCHEMA wns OWNER TO postgres;

SET search_path = wns, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;


CREATE TABLE notification (
    id integer NOT NULL,
    name text,
    description text
);

ALTER TABLE wns.notification OWNER TO postgres;

CREATE SEQUENCE notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE wns.notification_id_seq OWNER TO postgres;

ALTER SEQUENCE notification_id_seq OWNED BY notification.id;

CREATE TABLE registration (
    user_id_fk integer NOT NULL,
    not_id_fk integer NOT NULL,
    not_list text[]
);

ALTER TABLE wns.registration OWNER TO postgres;

CREATE TABLE "user" (
    id integer NOT NULL,
    username text,
    email text,
    twitter text,
    tel text,
    fax text,
    address text,
    zip integer,
    city text,
    state text,
    country text
);

ALTER TABLE wns."user" OWNER TO postgres;

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE wns.user_id_seq OWNER TO postgres;

ALTER SEQUENCE user_id_seq OWNED BY "user".id;

ALTER TABLE ONLY notification ALTER COLUMN id SET DEFAULT nextval('notification_id_seq'::regclass);

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);

ALTER TABLE ONLY notification
    ADD CONSTRAINT notification_name_key UNIQUE (name);

ALTER TABLE ONLY notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);

ALTER TABLE ONLY registration
    ADD CONSTRAINT registration_pkey PRIMARY KEY (user_id_fk, not_id_fk);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_email_key UNIQUE (email);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_username_key UNIQUE (username);

ALTER TABLE ONLY registration
    ADD CONSTRAINT not_id_fkey FOREIGN KEY (not_id_fk) REFERENCES notification(id);

ALTER TABLE ONLY registration
    ADD CONSTRAINT user_id_fkey FOREIGN KEY (user_id_fk) REFERENCES "user"(id) ON DELETE CASCADE;
