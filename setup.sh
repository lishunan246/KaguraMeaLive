#!/usr/bin/env bash

cp *.service /etc/systemd/system/
cp *.timer /etc/systemd/system/

systemctl daemon-reload