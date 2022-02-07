---
title: "An overhaul"
date: 2022-02-07T14:00:00+00:00
slug: 2022-02-07-overhaul
type: posts
draft: true
categories:
  - default
tags:
  - meta
---
This was long overdue but I've finally switched to
[a modern static site generator](https://gohugo.io/).
The
[old system](https://github.com/kahara/Async.fi/commits/91b4bd250e5ba97a105c0bcc26f310d9a5824bc4/site.py)
was written by myself in Python 2 many moons ago, and adding
[posts](https://past.async.fi)
consisted of writing plain HTML into a monolithic XML source file, then deploying
to S3 where Cloudfront served it from. Porting the Python 2 code to Python 3
would've likely been tedious, and would've still left me stuck with HTML.

Additionally, I've been moving my non-work efforts away from faraway clouds
(partly because of politics, partly because I get to deal with those enough
already on a daily basis, partly because of costs) and to a machine from
[a local operator](https://upcloud.com/signup/?promo=RY3367)
with presence within a few hops and a short ping from our home network.

The theme is
[smol](https://github.com/colorchestra/smol)
with some minor tweaks.
