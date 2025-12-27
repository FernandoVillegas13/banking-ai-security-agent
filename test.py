import threading
import requests

url = "http://localhost:8000/query"
headers = {"Content-Type": "application/json"}

payloads = [
    {"message": "hola como estas quien eres?", "session_id": "126", "category": "ventas"},
    {"message": "hola como estas quien eres?", "session_id": "127", "category": "ventas"}, 
    {"message": "hola como estas quien eres?", "session_id": "128", "category": "ventas"},
    {"message": "hola como estas quien eres?", "session_id": "129", "category": "ventas"},
    {"message": "hola como estas quien eres?", "session_id": "130", "category": "ventas"},
    {"message": "hola como estas quien eres?", "session_id": "131", "category": "ventas"}
]

def send(payload):
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"session_id={payload['session_id']} -> {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"session_id={payload['session_id']} -> Error: {e}")

if __name__ == "__main__":
    threads = [threading.Thread(target=send, args=(p,)) for p in payloads]
    for t in threads: t.start()
    for t in threads: t.join()