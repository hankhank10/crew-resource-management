import requests
import base64

url = "https://proxy.api.deepaffects.com/text/generic/api/v1/async/punctuate"

querystring = {"apikey":"idm6bCzQyQyraKfsGwGeRWnD7xV6wp1U", "webhook":"<WEBHOOK_URL>"}

payload = {"texts": ["so its more fluid than it is and you know its not the best kind of feedback right"]}

headers = {
    'Content-Type': "application/json",
}

response = requests.post(url, json=payload, headers=headers, params=querystring)

print(response.text)