### Postgres install

Lets issue the following commands to install the postgres sql db to our server.

You need to have sudo prompt

``` bash
dnf module list postgresql
dnf module enable postgresql:12
dnf install postgresql-server
postgresql-setup --initdb
systemctl start postgresql
systemctl enable postgresql
```