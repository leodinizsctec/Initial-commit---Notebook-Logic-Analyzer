#!/bin/bash
echo "=== Notebook Logic Analyzer - Setup ==="
[ "$EUID" -ne 0 ] && echo "❌ Use: sudo ./setup.sh" && exit 1
apt-get update && apt-get install -y build-essential python3 python3-pip
pip3 install numpy
cd src/capture && make && cd ../..
echo "✅ Pronto!"
