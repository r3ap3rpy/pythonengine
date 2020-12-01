### Postgres install

Lets issue the following commands to install the postgres sql db to our server.

You need to have sudo prompt

Now you can install the new repository.

``` bash
yum install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm -y 
dnf -qy module disable postgresql
dnf install -y postgresql13-server
/usr/pgsql-13/bin/postgresql-13-setup initdb
systemctl enable postgresql-13
systemctl start postgresql-13
```

Now we have to add the following line to the file */var/lib/pgsql/13/data/pg_hba.conf*

``` bash
host    all             all             0.0.0.0/0               md5
```

Now we have to modify the following line the file */var/lib/pgsql/13/data/postgresql.conf*

``` bash
listen_addresses = '*'
```

Finally restart the server.

``` bash
systemctl restart postgresql-13
```

Let's reset the postgres password!

``` bash
sudo -i -u postgres
psql -U postgres -c "alter user postgres with password 'postgres'"
```

Now on the webui you have to follow the instructions.

For windows you can download the [pgadmin](https://ftp.postgresql.org/pub/pgadmin/pgadmin4/v4.28/windows/pgadmin4-4.28-x64.exe) to have a web based acess!

This is the create script for the *users* table.

``` sql
-- Table: public.users

-- DROP TABLE public.users;

CREATE TABLE public.users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    email character varying COLLATE pg_catalog."default" NOT NULL,
    password character varying COLLATE pg_catalog."default" NOT NULL,
    level smallint NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.users
    OWNER to pyengine;
```

This is the create script for the *tools* table.

``` sql
-- Table: public.tools

-- DROP TABLE public.tools;

CREATE TABLE public.tools
(
    "Solution" character varying COLLATE pg_catalog."default" NOT NULL,
    "TaskList" character varying COLLATE pg_catalog."default" NOT NULL,
    "TaskPath" character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT tools_pkey PRIMARY KEY ("Solution")
)

TABLESPACE pg_default;

ALTER TABLE public.tools
    OWNER to pyengine;
```

This is the create script for the *requests* table.

``` sql
-- Table: public.requests

-- DROP TABLE public.requests;

CREATE TABLE public.requests
(
    "TaskID" integer NOT NULL DEFAULT nextval('"requests_TaskID_seq"'::regclass),
    "Requester" character varying COLLATE pg_catalog."default" NOT NULL,
    "Worker" character varying COLLATE pg_catalog."default" NOT NULL,
    "Solution" character varying COLLATE pg_catalog."default" NOT NULL,
    "Task" character varying COLLATE pg_catalog."default" NOT NULL,
    "Targets" character varying COLLATE pg_catalog."default" NOT NULL,
    "Extraargs" character varying COLLATE pg_catalog."default" NOT NULL,
    "Status" character varying COLLATE pg_catalog."default" NOT NULL,
    "Result" character varying COLLATE pg_catalog."default" NOT NULL,
    "SubmissionTime" date NOT NULL,
    CONSTRAINT requests_pkey PRIMARY KEY ("TaskID")
)

TABLESPACE pg_default;

ALTER TABLE public.requests
    OWNER to pyengine;
```

ODBC driver for [postgres](https://ftp.postgresql.org/pub/odbc/versions/msi/psqlodbc_13_00_0000-x64.zip) on windows systems.

The following scipt can be used to test out the functionality.

``` python
import psycopg2
conn = psycopg2.connect(dbname='pyengine',user='pyengine',password='pyengine!123',host='ansibler')
cur.execute("select * from users")
cur.fetchall()
```
