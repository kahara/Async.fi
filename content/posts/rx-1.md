---
title: "New receivers"
date: 2024-12-24T17:57:30+02:00
slug: 2024-12-24-rx-1
type: posts
draft: false
categories:
  - default
tags:
  - amateur-radio
  - rtl-sdr
---
The balconic setup is made up of the following substations, each consisting of
an RTL-SDR and a dedicated Raspberry Pi 4, for (hopefully!) round-the-clock
monitoring with [luarvique/openwebrx](https://github.com/luarvique/openwebrx):

* [6m.rx-1.async.fi](https://6m.rx-1.async.fi/)
* [2m.rx-1.async.fi](https://2m.rx-1.async.fi/)
* [70cm.rx-1.async.fi](https://70cm.rx-1.async.fi/)

On six meters, there's a simple vertical with no radials, a broadcast FM
notch filter, and an LNA.
VHF and UHF receivers share a Diamond SG7900 + a broadcast FM
notch filter over a splitter/combiner.

Six meter filter and amp are generic Nooelec parts, filter and splitter for
VHF and UHF came from [SV1AFN](https://www.sv1afn.com/en/products/).
Six meter receiver is a Nooelec dongle, VHF and UHF ones are
["RTL-SDR Blog V4"](https://www.rtl-sdr.com/v4/).
Cables were tailor-made from Aircell 7 by [Paratronic](https://paratronic.fi/).

So far things seem to have been working adequately well, let's see.
