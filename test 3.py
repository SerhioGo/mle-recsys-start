import requests
recommendations_url = "http://127.0.0.1:900"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# params = {"user_id": 1291248, 'k': 3}

# resp = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
# if resp.status_code == 200:
#     online_recs = resp.json()
# else:
#     online_recs = None
#     print(f"status code: {resp.status_code}")

# print(online_recs)

params = {"user_id": 1291248, 'k': 3}

resp = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
online_recs = resp.json()
    
print(online_recs)