#!/bin/bash
cd /home/claude/twocups
python3 film.py scenes scenes day90 day14 day30 cold card close > r1.log 2>&1 &
python3 film.py scenes scenes day1 days day8 day40 day60 sign > r2.log 2>&1 &
wait
