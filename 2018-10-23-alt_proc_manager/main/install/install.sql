--
-- PostgreSQL database dump
--

-- Dumped from database version 10.5
-- Dumped by pg_dump version 10.5

-- Started on 2018-11-13 18:23:30

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
-- TOC entry 2893 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 196 (class 1259 OID 17067)
-- Name: cmds; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.cmds (
    cmd_id integer NOT NULL,
    name character varying NOT NULL,
    params json,
    status character varying DEFAULT 'WAIT'::character varying NOT NULL,
    error character varying,
    ctime timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cmds OWNER TO alt_proc;

--
-- TOC entry 197 (class 1259 OID 17075)
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
-- TOC entry 2894 (class 0 OID 0)
-- Dependencies: 197
-- Name: cmds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.cmds_id_seq OWNED BY public.cmds.cmd_id;


--
-- TOC entry 198 (class 1259 OID 17077)
-- Name: events; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.events (
    event_id integer NOT NULL,
    task_id integer NOT NULL,
    param character varying,
    ctime timestamp without time zone DEFAULT now() NOT NULL,
    status character varying DEFAULT 'WAIT'::character varying NOT NULL,
    params json
);


ALTER TABLE public.events OWNER TO alt_proc;

--
-- TOC entry 199 (class 1259 OID 17085)
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
-- TOC entry 2895 (class 0 OID 0)
-- Dependencies: 199
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.event_id;


--
-- TOC entry 200 (class 1259 OID 17087)
-- Name: jobs; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.jobs (
    job_id integer NOT NULL,
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
-- TOC entry 201 (class 1259 OID 17096)
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
-- TOC entry 2896 (class 0 OID 0)
-- Dependencies: 201
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.job_id;


--
-- TOC entry 202 (class 1259 OID 17098)
-- Name: msgs; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.msgs (
    msg_id integer NOT NULL,
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
-- TOC entry 203 (class 1259 OID 17109)
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
-- TOC entry 2897 (class 0 OID 0)
-- Dependencies: 203
-- Name: msgs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.msgs_id_seq OWNED BY public.msgs.msg_id;


--
-- TOC entry 204 (class 1259 OID 17111)
-- Name: runs; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.runs (
    run_id integer NOT NULL,
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
-- TOC entry 205 (class 1259 OID 17118)
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
-- TOC entry 2898 (class 0 OID 0)
-- Dependencies: 205
-- Name: runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.runs_id_seq OWNED BY public.runs.run_id;


--
-- TOC entry 206 (class 1259 OID 17120)
-- Name: scripts; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.scripts (
    script_id integer NOT NULL,
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
-- TOC entry 207 (class 1259 OID 17128)
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
-- TOC entry 2899 (class 0 OID 0)
-- Dependencies: 207
-- Name: scripts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.scripts_id_seq OWNED BY public.scripts.script_id;


--
-- TOC entry 208 (class 1259 OID 17130)
-- Name: tasks; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public.tasks (
    task_id integer NOT NULL,
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
-- TOC entry 209 (class 1259 OID 17140)
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
-- TOC entry 2900 (class 0 OID 0)
-- Dependencies: 209
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alt_proc
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.task_id;


--
-- TOC entry 210 (class 1259 OID 17142)
-- Name: values; Type: TABLE; Schema: public; Owner: alt_proc
--

CREATE TABLE public."values" (
    name character varying NOT NULL,
    value character varying
);


ALTER TABLE public."values" OWNER TO alt_proc;

--
-- TOC entry 2720 (class 2604 OID 17148)
-- Name: cmds cmd_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.cmds ALTER COLUMN cmd_id SET DEFAULT nextval('public.cmds_id_seq'::regclass);


--
-- TOC entry 2723 (class 2604 OID 17149)
-- Name: events event_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.events ALTER COLUMN event_id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- TOC entry 2727 (class 2604 OID 17150)
-- Name: jobs job_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.jobs ALTER COLUMN job_id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- TOC entry 2733 (class 2604 OID 17151)
-- Name: msgs msg_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.msgs ALTER COLUMN msg_id SET DEFAULT nextval('public.msgs_id_seq'::regclass);


--
-- TOC entry 2735 (class 2604 OID 17152)
-- Name: runs run_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.runs ALTER COLUMN run_id SET DEFAULT nextval('public.runs_id_seq'::regclass);


--
-- TOC entry 2738 (class 2604 OID 17153)
-- Name: scripts script_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.scripts ALTER COLUMN script_id SET DEFAULT nextval('public.scripts_id_seq'::regclass);


--
-- TOC entry 2743 (class 2604 OID 17154)
-- Name: tasks task_id; Type: DEFAULT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.tasks ALTER COLUMN task_id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- TOC entry 2745 (class 2606 OID 17156)
-- Name: cmds cmds_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.cmds
    ADD CONSTRAINT cmds_pk PRIMARY KEY (cmd_id);


--
-- TOC entry 2747 (class 2606 OID 17158)
-- Name: events events_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pk PRIMARY KEY (event_id);


--
-- TOC entry 2749 (class 2606 OID 17160)
-- Name: jobs jobs_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pk PRIMARY KEY (job_id);


--
-- TOC entry 2751 (class 2606 OID 17162)
-- Name: msgs msgs_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.msgs
    ADD CONSTRAINT msgs_pk PRIMARY KEY (msg_id);


--
-- TOC entry 2753 (class 2606 OID 17164)
-- Name: runs runs_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_pk PRIMARY KEY (run_id);


--
-- TOC entry 2755 (class 2606 OID 17166)
-- Name: scripts scripts_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.scripts
    ADD CONSTRAINT scripts_pk PRIMARY KEY (script_id);


--
-- TOC entry 2757 (class 2606 OID 17168)
-- Name: tasks tasks_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pk PRIMARY KEY (task_id);


--
-- TOC entry 2759 (class 2606 OID 17172)
-- Name: values values_pk; Type: CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public."values"
    ADD CONSTRAINT values_pk PRIMARY KEY (name);


--
-- TOC entry 2760 (class 2606 OID 17173)
-- Name: events events_tasks_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_tasks_fk FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2761 (class 2606 OID 17178)
-- Name: jobs jobs_events_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_events_fk FOREIGN KEY (event_id) REFERENCES public.events(event_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2762 (class 2606 OID 17183)
-- Name: msgs msgs_scripts_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.msgs
    ADD CONSTRAINT msgs_scripts_fk FOREIGN KEY (script_id) REFERENCES public.scripts(script_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2763 (class 2606 OID 17188)
-- Name: runs runs_scripts_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_scripts_fk FOREIGN KEY (script_id) REFERENCES public.scripts(script_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2764 (class 2606 OID 17193)
-- Name: scripts scripts_jobs_fk; Type: FK CONSTRAINT; Schema: public; Owner: alt_proc
--

ALTER TABLE ONLY public.scripts
    ADD CONSTRAINT scripts_jobs_fk FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2018-11-13 18:23:31

--
-- PostgreSQL database dump complete
--
