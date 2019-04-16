# RabbitMQ Timeout

Figuring out how to set timeout on `basic_publish` so that
client won't wait for a long time.

# Quickstart

```
pip install -r requirements.txt
toxiproxy-server
toxiproxy-cli create rabbitmq --listen localhost:5670 --upstream localhost:5672
```
toxiproxy is https://github.com/Shopify/toxiproxy


Below connects to toxiproxy and publishes a message every second:
```
python
>>> import pika_test
>>> pika_test.Client().run()
```

Once it's publishing messages, set proxy's latency:
```
toxiproxy-cli toxic add rabbitmq -t latency -a latency=10000
```


