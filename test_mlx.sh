#!/bin/bash
# Test MLX server

python3 << 'PYSCRIPT'
import json
data = {"model":"nightmedia/Qwen3-VLTO-8B-Instruct-qx86x-hi-mlx","messages":[{"role":"user","content":"Hello, say hi back in one sentence"}]}
with open('/tmp/test.json', 'w') as f:
    json.dump(data, f)
print("JSON written:", json.dumps(data))
PYSCRIPT

echo "Testing MLX server..."
curl --http0.9 -s -X POST http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d @/tmp/test.json
