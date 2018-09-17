# About

Attempts at load balancing postgres reads using various ways.

# Quickstart

```
$ docker-compose build

# start two postgres
$ docker-compose up pg1
$ docker-compose up pg2

# start dns server (for pgbouncer load balancing)
$ docker-compose up dnsmasq

# test pgbouncer
$ docker-compose up pgbouncer

$ psql --host=localhost --username=postgres --password test
# password is postgres

# test pgpool (must kill pgbouncer service first)
$ docker-compose up pgpool
```

# Status

- Round robin works:
    ```
    $ docker-compose exec pgbouncer sh
    $ psql --host=pg --username=postgres --password test
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
- But, connecting directly to pgbouncer does not work:
    ```
    $ psql --host=localhost --username=postgres --password  test
    Password for user postgres: 
    psql: ERROR:  no such user: postgres

    # pgbouncer log
    pgbouncer_1  | 2018-09-13 21:21:14.168 1 WARNING C-0x5620393c5450: (nodb)/(nouser)@192.168.100.1:39942 pooler error: no such user: postgres
    ```
    - Need to figure out how to configure pgbouncer auth to be passthrough
- pgpool does not work either even though backend nodes are reachable.
    ```
    pgpool_1     | 2018-09-13 21:23:21: pid 25: FATAL:  pgpool is not accepting any new connections
    pgpool_1     | 2018-09-13 21:23:21: pid 25: DETAIL:  all backend nodes are down, pgpool requires at least one valid node
    pgpool_1     | 2018-09-13 21:23:21: pid 25: HINT:  repair the backend nodes and restart pgpool

    $ docker-compose exec pgpool sh
    $ ping pg1
    PING pg1 (192.168.100.3): 56 data bytes
    64 bytes from 192.168.100.3: seq=0 ttl=64 time=0.092 ms
    $ ping pg2
    PING pg2 (192.168.100.4): 56 data bytes
    64 bytes from 192.168.100.4: seq=0 ttl=64 time=0.143 ms
    ```
    - Need to figure out how to configure pgpool.
