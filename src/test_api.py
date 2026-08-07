import requests
import time

base = 'http://127.0.0.1:8000'

# Wait for server to be ready (indexing can take time)
for _ in range(15):
    try:
        r = requests.get(f'{base}/health', timeout=2)
        print('health', r.status_code, r.text)
        break
    except Exception as e:
        print('waiting for server...', e)
        time.sleep(1)

# Test ask endpoint (send JSON)
try:
    r = requests.post(f'{base}/ask', json={'question':'What is bubble sort?'}, timeout=30)
    print('ask', r.status_code, r.text)
except Exception as e:
    print('ask failed', e)
