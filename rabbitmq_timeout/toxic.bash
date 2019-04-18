#!/bin/bash

case "$1" in
	init)
	toxiproxy-cli create rabbitmq --listen localhost:5670 --upstream localhost:5672
	;;
	add)
	toxiproxy-cli toxic add rabbitmq -n latency_downstream -t latency -a latency=10000
	toxiproxy-cli toxic add rabbitmq -n bandwidth_downstream -t bandwidth -a rate=1
	;;
	remove)
	toxiproxy-cli toxic remove rabbitmq -n latency_downstream
	toxiproxy-cli toxic remove rabbitmq -n bandwidth_downstream
	;;
esac

