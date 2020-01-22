#!/usr/bin/env bash

PIDFILE="/Users/gilbeyruth/Documents/nubank/saltServer.pid"

if [ -e "${PIDFILE}" ] && (ps -u $USER -f | grep "[ ]$(cat ${PIDFILE})[ ]"); then
    echo "Already running."
    exit 99
fi

nohup python /Users/gilbeyruth/Documents/nubank/authorize.py < operations1