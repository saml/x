# About

Attempts at load balancing postgres reads using various ways.
Currently, only DNS round robin and HAProxy works.
I could not get pgpool and pgbouncer to load balance.

# Quickstart

```
$ docker-compose build

# start two postgres
$ docker-compose up pg1
$ docker-compose up pg2

# start dns server (for pgbouncer load balancing)
$ docker-compose up dnsmasq

# start middleware
# only only one of below:

# test pgbouncer
$ docker-compose up pgbouncer

# test pgpool
$ docker-compose up pgpool

# test haproxy
$ docker-compose up haproxy
```

Connect to middleware:

```
$ psql --host=localhost --username=postgres --password test
# password is postgres

test=# select inet_server_addr();
```

# Status

Name|Load balance|Failover|Note
----|-------------|-------|----
DNS round robin|Yes|Yes|When db goes down, reconnection could take a long time since psql tries IP that's unhealthy then falls back to the second one.
haproxy|Yes|Yes|Failover is quick, there is no delay observed in DNS round robin
pgpool|No|No|Cannot set up as transparent proxy (authentication is passthrough)
pgbouncer|No|No|Cannot set up as transparent proxy

To test load balance, connect to middleware using `psql` and check server address.
And reconnect using `\c` and check it connects to different server.

To test failover, connect to middleware, check server address. And, kill the server.
And, reconnect and see if it connects to different server.


## DNS round robin

DNS round robin can be tested inside pgbouncer container
(only pgbouncer is configured with round robin DNS):

```
$ docker-compose exec pgbouncer sh
# pg is host name that round robins two servers.
> psql --host=pg --username=postgres --password test
test=# select inet_server_addr();
inet_server_addr 
------------------
192.168.100.4

test=# \c

test=# select inet_server_addr();
inet_server_addr 
------------------
192.168.100.3
```

### HAProxy

HAProxy can be tested from host (not inside container):

```
$ psql --host=localhost --username=postgres --password test
```
