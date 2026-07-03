--
-- PostgreSQL database dump
--

-- Dumped from database version 15.18
-- Dumped by pg_dump version 15.18

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_id;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    password_hash character varying NOT NULL,
    role character varying NOT NULL,
    is_active boolean
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, role, is_active) FROM stdin;
1	catherine	$2b$12$wJBlOIL0cz2evYDUGkwxiOXnYXu5Y5XwEg5WN4mM2SCR3sBtYyQqa	Project_Admin	t
2	jack	$2b$12$QAVWGC/mIt8Be35NFesqhOFHHglmyjJUST35To0ZcJ.6ZRag/ILvu	Platform_Admin	t
3	alex	$2b$12$/tC5Gm8Yvi0hxMldkzBO/uHrVK73GeMNPRame45lWyqMDJNhq1NHm	Project_Architect	t
4	ben	$2b$12$JbpPm9JlqgO2xz.wtk28wOyWpHgjazkY5hNseZ8ZkbfwOzw3XfaEm	SRE	t
5	david	$2b$12$ocbNZBgos6NRHS22kg6Cj.ZfOMcvbHN5e/Umuw3cw8b5bOwuURb56	FinOps_Analyst	t
6	elena	$2b$12$QXdNBq6fmJUmS3SvvluVR.0T30jLc5fMpD982yXUGQqCAn4J4uCe.	Platform_Engineer	t
7	fiona	$2b$12$7h5qFYyGx/yqipgDIXvRr.7vijXKflYIJJMRiwCLp9GoJJ/oOt46O	Security_Reviewer	t
8	george	$2b$12$D.1Wi5R1l3qJhYgJ6TYEGeW2RESxEQv0uX2BLSH5/cci6oQt/9ypW	Ops_Lead	t
9	hannah	$2b$12$.shhPx2IxoevD2r49F8IbujQms.oVihjix4tsbsGIMUFhs2fexyyK	Project_Editor	t
10	ian	$2b$12$Tr0nydTrzzUOkxlXNnoB8epPSo00dcZOJ451bq.wAPxpookfozWtm	Developer	t
11	karen	$2b$12$jj4E4Rupj27GVRkK8sVUS.My9H26powFZKPBkSvuw3yTSWg52z7JO	Platform_Owner	t
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 11, true);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- PostgreSQL database dump complete
--
