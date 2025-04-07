import json
import os

FILENAME = "requests.json"

def load_requests():
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r") as f:
        return json.load(f)

def save_requests(requests):
    with open(FILENAME, "w") as f:
        json.dump(requests, f, indent=4)

def add_request(request):
    requests = load_requests()
    requests.append(request)
    save_requests(requests)

def update_request_status(request_id, new_status):
    requests = load_requests()
    for req in requests:
        if req["id"] == request_id:
            req["status"] = new_status
            break
    save_requests(requests)

def update_summary(request_id, summary):
    requests = load_requests()
    for req in requests:
        if req["id"] == request_id:
            req["summary"] = summary
            break
    save_requests(requests)
