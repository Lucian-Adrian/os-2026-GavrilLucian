#!/bin/bash
# Test script for Linux args implementation
set -e

echo "=== Compiling args_linux.c ==="
gcc -Wall -O2 -o args args_linux.c

echo "=== Test 1: Multiple whitespace ==="
./args one   two   three

echo "=== Test 2: Wildcard and quotes ==="
./args *.c "x y"

echo "=== Test 3: Environment variable ==="
./args "$HOME"

echo "=== Test 4: Single quotes ==="
./args 'single quoted'

echo "=== All Linux args tests completed successfully ==="
