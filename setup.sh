#!/usr/bin/env bash

cp *.service /etc/systemd/system/
systemctl daemon-reload