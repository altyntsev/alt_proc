--
-- PostgreSQL database dump
--

-- Dumped from database version 10.5
-- Dumped by pg_dump version 10.5

-- Started on 2018-10-27 16:41:42

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 1 (class 3079 OID 12924)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2896 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 196 (class 1259 OID 16767)
-- Name: cmds; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.cmds (
    id integer NOT NULL,
    name character varying NOT NULL,
    params json,
    status character varying DEFAULT 'WAIT'::character varying NOT NULL,
    error character varying,
    ctime timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cmds OWNER TO alt_proc;

--
-- TOC entry 197 (class 1259 OID 16774)
-- Name: cmds_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.cmds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cmds_id_seq OWNER TO alt_proc;

--
-- TOC entry 2897 (class 0 OID 0)
-- Dependencies: 197
-- Name: cmds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.cmds_id_seq OWNED BY public.cmds.id;


--
-- TOC entry 198 (class 1259 OID 16776)
-- Name: events; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.events (
    id integer NOT NULL,
    task_id integer NOT NULL,
    param character varying DEFAULT ''::character varying,
    ctime timestamp without time zone DEFAULT now() NOT NULL,
    status character varying DEFAULT 'WAIT'::character varying NOT NULL,
    params json
);


ALTER TABLE public.events OWNER TO alt_proc;

--
-- TOC entry 199 (class 1259 OID 16784)
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq OWNER TO alt_proc;

--
-- TOC entry 2898 (class 0 OID 0)
-- Dependencies: 199
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- TOC entry 200 (class 1259 OID 16786)
-- Name: jobs; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    status character varying DEFAULT 'WAIT'::character varying NOT NULL,
    result character varying,
    todo boolean DEFAULT false NOT NULL,
    event_id integer,
    ctime timestamp without time zone DEFAULT now() NOT NULL,
    stime timestamp without time zone,
    etime timestamp without time zone,
    mtime timestamp without time zone NOT NULL,
    run_at timestamp without time zone,
    os_pid integer
);


ALTER TABLE public.jobs OWNER TO alt_proc;

--
-- TOC entry 201 (class 1259 OID 16795)
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.jobs_id_seq OWNER TO alt_proc;

--
-- TOC entry 2899 (class 0 OID 0)
-- Dependencies: 201
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- TOC entry 202 (class 1259 OID 16797)
-- Name: msgs; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.msgs (
    id integer NOT NULL,
    msg character varying NOT NULL,
    type character varying NOT NULL,
    active boolean DEFAULT true NOT NULL,
    script_id integer NOT NULL,
    stime timestamp without time zone NOT NULL,
    etime timestamp without time zone NOT NULL,
    n_runs integer DEFAULT 1 NOT NULL,
    todo boolean DEFAULT false NOT NULL,
    read boolean DEFAULT false NOT NULL,
    send boolean DEFAULT false NOT NULL
);


ALTER TABLE public.msgs OWNER TO alt_proc;

--
-- TOC entry 203 (class 1259 OID 16808)
-- Name: msgs_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.msgs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.msgs_id_seq OWNER TO alt_proc;

--
-- TOC entry 2900 (class 0 OID 0)
-- Dependencies: 203
-- Name: msgs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.msgs_id_seq OWNED BY public.msgs.id;


--
-- TOC entry 204 (class 1259 OID 16810)
-- Name: runs; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.runs (
    id integer NOT NULL,
    script_id integer NOT NULL,
    result character varying,
    stime timestamp without time zone,
    etime timestamp without time zone,
    restart_after integer,
    msgs character varying,
    debug boolean DEFAULT false
);


ALTER TABLE public.runs OWNER TO alt_proc;

--
-- TOC entry 205 (class 1259 OID 16817)
-- Name: runs_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.runs_id_seq OWNER TO alt_proc;

--
-- TOC entry 2901 (class 0 OID 0)
-- Dependencies: 205
-- Name: runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.runs_id_seq OWNED BY public.runs.id;


--
-- TOC entry 206 (class 1259 OID 16819)
-- Name: scripts; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.scripts (
    id integer NOT NULL,
    job_id integer NOT NULL,
    iscript integer,
    cmd character varying NOT NULL,
    name character varying NOT NULL,
    status character varying DEFAULT 'WAIT'::character varying NOT NULL,
    result character varying,
    todo boolean DEFAULT false NOT NULL,
    last_run_id integer
);


ALTER TABLE public.scripts OWNER TO alt_proc;

--
-- TOC entry 207 (class 1259 OID 16827)
-- Name: scripts_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.scripts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scripts_id_seq OWNER TO alt_proc;

--
-- TOC entry 2902 (class 0 OID 0)
-- Dependencies: 207
-- Name: scripts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.scripts_id_seq OWNED BY public.scripts.id;


--
-- TOC entry 208 (class 1259 OID 16829)
-- Name: tasks; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    type character varying NOT NULL,
    name character varying NOT NULL,
    status character varying DEFAULT 'PAUSE'::character varying NOT NULL,
    project character varying NOT NULL,
    period integer,
    priority integer DEFAULT 0 NOT NULL,
    n_fatals integer DEFAULT 1 NOT NULL,
    n_runs integer DEFAULT 1 NOT NULL,
    resources json
);


ALTER TABLE public.tasks OWNER TO alt_proc;

--
-- TOC entry 209 (class 1259 OID 16839)
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: alt_proc
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO alt_proc;

--
-- TOC entry 2903 (class 0 OID 0)
-- Dependencies: 209
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- TOC entry 210 (class 1259 OID 16841)
-- Name: values; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public."values" (
    name character varying NOT NULL,
    value character varying
);


ALTER TABLE public."values" OWNER TO alt_proc;

--
-- TOC entry 2719 (class 2604 OID 16847)
-- Name: cmds id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.cmds ALTER COLUMN id SET DEFAULT nextval('public.cmds_id_seq'::regclass);


--
-- TOC entry 2723 (class 2604 OID 16848)
-- Name: events id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- TOC entry 2728 (class 2604 OID 16849)
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- TOC entry 2734 (class 2604 OID 16850)
-- Name: msgs id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.msgs ALTER COLUMN id SET DEFAULT nextval('public.msgs_id_seq'::regclass);


--
-- TOC entry 2736 (class 2604 OID 16851)
-- Name: runs id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.runs ALTER COLUMN id SET DEFAULT nextval('public.runs_id_seq'::regclass);


--
-- TOC entry 2739 (class 2604 OID 16852)
-- Name: scripts id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.scripts ALTER COLUMN id SET DEFAULT nextval('public.scripts_id_seq'::regclass);


--
-- TOC entry 2744 (class 2604 OID 16853)
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- TOC entry 2746 (class 2606 OID 16855)
-- Name: cmds cmds_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.cmds
    ADD CONSTRAINT cmds_pk PRIMARY KEY (id);


--
-- TOC entry 2748 (class 2606 OID 16857)
-- Name: events events_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pk PRIMARY KEY (id);


--
-- TOC entry 2750 (class 2606 OID 16859)
-- Name: jobs jobs_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pk PRIMARY KEY (id);


--
-- TOC entry 2752 (class 2606 OID 16861)
-- Name: msgs msgs_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.msgs
    ADD CONSTRAINT msgs_pk PRIMARY KEY (id);


--
-- TOC entry 2754 (class 2606 OID 16863)
-- Name: runs runs_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_pk PRIMARY KEY (id);


--
-- TOC entry 2756 (class 2606 OID 16865)
-- Name: scripts scripts_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.scripts
    ADD CONSTRAINT scripts_pk PRIMARY KEY (id);


--
-- TOC entry 2758 (class 2606 OID 16867)
-- Name: tasks tasks_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pk PRIMARY KEY (id);


--
-- TOC entry 2760 (class 2606 OID 16869)
-- Name: tasks tasks_un; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_un UNIQUE (name);


--
-- TOC entry 2762 (class 2606 OID 16871)
-- Name: values values_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public."values"
    ADD CONSTRAINT values_pk PRIMARY KEY (name);


--
-- TOC entry 2763 (class 2606 OID 16872)
-- Name: events events_tasks_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_tasks_fk FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2764 (class 2606 OID 16877)
-- Name: jobs jobs_events_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_events_fk FOREIGN KEY (event_id) REFERENCES public.events(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2765 (class 2606 OID 16882)
-- Name: msgs msgs_scripts_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.msgs
    ADD CONSTRAINT msgs_scripts_fk FOREIGN KEY (script_id) REFERENCES public.scripts(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2766 (class 2606 OID 16887)
-- Name: runs runs_scripts_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_scripts_fk FOREIGN KEY (script_id) REFERENCES public.scripts(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2767 (class 2606 OID 16892)
-- Name: scripts scripts_jobs_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.scripts
    ADD CONSTRAINT scripts_jobs_fk FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2018-10-27 16:41:43

--
-- PostgreSQL database dump complete
--
