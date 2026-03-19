import requests

base_url = 'https://app.map.kakao.com/route/carset/mobility.json'

params = {
    'origin': '127.37888948493487,36.38793945312501',
    'destination': '127.04669593,37.59267542',
}

response = requests.get(base_url, params=params)
print(response.text)

print(response.json()["results"][0]["summary"]["fare"]["taxi"])
