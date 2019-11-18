# About

Using BlockingConnection to publish messages infrequently results in broker closing the connection
because heartbeat isn't sent to the broker.

# Quickstart

```
# Start broker
docker run --rm --publish '5672:5672' --publish '15672:15672' rabbitmq:3.7-management-alpine

# Start test
python pika_heartbeat.py --heartbeat 10

# Broker closes connection
2019-11-18 16:23:41.414 [error] <0.685.0> closing AMQP connection <0.685.0> (172.17.0.1:43142 -> 172.17.0.2:5672):
missed heartbeats from client, timeout: 10s

# Test fails on second publish (after long sleep)
2019-11-18 11:24:01,471 ERROR pika.adapters.blocking_connection Unexpected connection close detected: StreamLostError: ('Transport indicated EOF',)
Traceback (most recent call last):
  File "pika_heartbeat.py", line 45, in <module>
    main()
  File "pika_heartbeat.py", line 41, in main
    ch.basic_publish("", "test", "")  # this is expected to fail
  File "/src/github.com/saml/x/pika_heartbeat/venv/lib64/python3.7/site-packages/pika/adapters/blocking_connection.py", line 2248, in basic_publish
    self._flush_output()
  File "/src/github.com/saml/x/pika_heartbeat/venv/lib64/python3.7/site-packages/pika/adapters/blocking_connection.py", line 1336, in _flush_output
    self._connection._flush_output(lambda: self.is_closed, *waiters)
  File "/src/github.com/saml/x/pika_heartbeat/venv/lib64/python3.7/site-packages/pika/adapters/blocking_connection.py", line 522, in _flush_output
    raise self._closed_result.value.error
pika.exceptions.StreamLostError: Transport indicated EOF
```
