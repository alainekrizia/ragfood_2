#!/usr/bin/env python3
"""Test script for RAG Food Knowledge Assistant"""

import subprocess
import sys

# Test Query
test_query = "Tell me about sushi"

# Run the app and send a query
process = subprocess.Popen(
    [sys.executable, "rag_run_upstash.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8'
)

try:
    # Send query and exit command
    stdout, stderr = process.communicate(
        input=f"{test_query}\nexit\n",
        timeout=60
    )
    
    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)
        
except subprocess.TimeoutExpired:
    process.kill()
    stdout, stderr = process.communicate()
    print("⚠️ Test timed out")
    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)
