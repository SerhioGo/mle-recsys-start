import requests
recommendations_url = "http://127.0.0.1:8000"
events_store_url = "http://127.0.0.1:8020"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

user_id = 1291248
event_item_ids = [41899, 102868, 5472, 5907]

resp = requests.post(events_store_url + "/put", 
                         headers=headers, 
                         params={"user_id": 1291248, "item_id": 41899})
result = resp.json()
print(result)

params = {"user_id": user_id, 'k': 1}
rekss = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
result_2 = rekss.json()
print(result_2)