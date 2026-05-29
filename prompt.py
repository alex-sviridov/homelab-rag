#!/usr/bin/env python3

import sys
from pathlib import Path
import requests

if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
else:
    prompt = input("Enter your prompt: ")

system_prompt = Path("system.txt").read_text()

response = requests.post("http://localhost:11434/api/chat", json={
    "model": "qwen3.5:2b",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ],
    "think": False,
    "stream": False,
})

response.raise_for_status()
print(response.json()["message"]["content"])
