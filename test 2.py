# import requests

# events_store_url = "http://127.0.0.1:8020"

# headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# params = {"user_id": 1127794, "item_id": 4731479}

# resp = requests.post(events_store_url + "/put", headers=headers, params=params)
# if resp.status_code == 200:
#     result = resp.json()
# else:
#     result = None
#     print(f"status code: {resp.status_code}")
    
# print(result)

import requests

events_store_url = "http://127.0.0.1:8020"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params={"user_id": 1127794, "k": 1}

resp = requests.post(events_store_url + "/get", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
else:
    result = None
    print(f"status code: {resp.status_code}")
    
print(result) 