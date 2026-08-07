#!/usr/bin/env bash
set -e

mkdir -p ../bin

gcc -O2 -Wall -shared -fPIC -o ../bin/pulse_loader.so pulse_loader.c
gcc -O2 -Wall -shared -fPIC -o ../bin/pulse_math.so pulse_math.c -lm

echo "Build complete."