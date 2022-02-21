---
title: "go-gnssaggr"
date: 2022-02-21T20:00:00+00:00
slug: 2022-02-21-go-gnssaggr
type: posts
draft: false
categories:
  - default
tags:
  - gnss
  - golang
---
[![](/illustration/gnssaggr-grafana.png)](/illustration/gnssaggr-grafana.png)

One of the nodes in my home Kubernetes cluster is running
[gpsd](https://github.com/kahara/docker-gpsd),
and has a
[cheap GNSS receiver](https://www.aliexpress.com/item/32816656706.html)
connected to it. Recording what the receiver sees and presenting that in a Grafana dashboard sounded like a nice idea.
I wanted to use Prometheus, which is already running, for this.

Main lesson:
[pay attention](https://github.com/kahara/go-gnssaggr/commit/411c67ca9b0f3d298b82c56c2dbef2941c141dc4)
when sending stuff on a Go channel; `go run -race` helped here.

[The repo](https://github.com/kahara/go-gnssaggr)
has more details.
See also: the
[Galmon project](https://galmon.eu/), where another one of my nodes with the same kind of cheap receiver is feeding.
